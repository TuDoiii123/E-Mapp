"""
Database connection and configuration for PostgreSQL backend
"""
import os
from urllib.parse import quote_plus
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.pool import NullPool
from sqlalchemy import text
from logger import get_logger

log = get_logger('db')
db  = SQLAlchemy()


def get_db_url():
    """Construct PostgreSQL connection URL from environment variables"""
    db_host     = os.getenv('DB_HOST', 'localhost').strip()
    db_port     = os.getenv('DB_PORT', '5432').strip()
    db_name     = os.getenv('DB_NAME', 'postgres').strip()
    db_user     = os.getenv('DB_USER', 'postgres').strip()
    db_password = os.getenv('DB_PASSWORD', '').strip()

    # URL-encode password để xử lý ký tự đặc biệt (@, #, %, ...)
    encoded_pw = quote_plus(db_password)

    return f'postgresql://{db_user}:{encoded_pw}@{db_host}:{db_port}/{db_name}'


def init_db(app):
    """Initialize database with Flask app"""
    app.config['SQLALCHEMY_DATABASE_URI'] = get_db_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 3600,
    }
    
    db.init_app(app)
    
    with app.app_context():
        # Create any SQLAlchemy models (if defined) and ensure 'users' table exists
        try:
            db.create_all()
        except Exception as e:
            # non-fatal: continue to ensure users table via raw SQL
            log.warning(f'db.create_all() failed: {e}')

        # Run explicit DDL to ensure users table exists for raw SQL access
        try:
            users_ddl = text('''
            CREATE TABLE IF NOT EXISTS public.users (
              id VARCHAR(80) PRIMARY KEY,
              cccd_number VARCHAR(50) UNIQUE,
              full_name VARCHAR(255),
              date_of_birth VARCHAR(50),
              phone VARCHAR(50),
              email VARCHAR(255) UNIQUE,
              password VARCHAR(255),
              role VARCHAR(50) NOT NULL DEFAULT 'citizen',
              is_vneid_verified BOOLEAN NOT NULL DEFAULT FALSE,
              vneid_id VARCHAR(255),
              address TEXT NOT NULL DEFAULT '',
              avatar_url VARCHAR(500) NOT NULL DEFAULT '',
              created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
              updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
            CREATE INDEX IF NOT EXISTS idx_users_cccd ON public.users(cccd_number);
            ''')
            db.session.execute(users_ddl)
            db.session.commit()
        except Exception as e:
            log.warning(f'Ensuring users table failed: {e}')

        # Migrate existing users table — add new columns if absent
        try:
            migrate_users_ddl = text('''
            ALTER TABLE public.users ADD COLUMN IF NOT EXISTS address TEXT NOT NULL DEFAULT '';
            ALTER TABLE public.users ADD COLUMN IF NOT EXISTS avatar_url VARCHAR(500) NOT NULL DEFAULT '';
            ''')
            db.session.execute(migrate_users_ddl)
            db.session.commit()
        except Exception as e:
            log.warning(f'Migrating users table (address/avatar_url) failed: {e}')

        # RAG chatbot + CAG cache tables
        try:
            rag_ddl = text('''
            CREATE TABLE IF NOT EXISTS public.chat_sessions (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(120) UNIQUE NOT NULL,
                first_message_summary TEXT,
                created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS public.conversation_history (
                id SERIAL PRIMARY KEY,
                session_id VARCHAR(120) NOT NULL
                    REFERENCES public.chat_sessions(session_id) ON DELETE CASCADE,
                user_message TEXT NOT NULL,
                bot_response TEXT,
                timestamp TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_conv_session
                ON public.conversation_history(session_id);
            CREATE INDEX IF NOT EXISTS idx_conv_timestamp
                ON public.conversation_history(timestamp);

            CREATE TABLE IF NOT EXISTS public.query_results (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER
                    REFERENCES public.conversation_history(id) ON DELETE CASCADE,
                query_text TEXT,
                response_text TEXT,
                retrieved_docs TEXT,
                model_name VARCHAR(100),
                timestamp TIMESTAMPTZ NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS public.agency_queue_realtime (
                agency_id     VARCHAR(120) PRIMARY KEY,
                total_waiting INTEGER NOT NULL DEFAULT 0,
                total_serving INTEGER NOT NULL DEFAULT 0,
                load_level    VARCHAR(20) NOT NULL DEFAULT 'low',
                updated_at    TIMESTAMPTZ NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS public.rag_semantic_cache (
                id          SERIAL PRIMARY KEY,
                query_hash  VARCHAR(64) UNIQUE NOT NULL,
                query_text  TEXT NOT NULL,
                query_vector TEXT NOT NULL,
                answer_text TEXT NOT NULL,
                hit_count   INTEGER NOT NULL DEFAULT 0,
                created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
                last_hit_at TIMESTAMPTZ NOT NULL DEFAULT now(),
                expires_at  TIMESTAMPTZ NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_cache_expires
                ON public.rag_semantic_cache(expires_at);
            CREATE INDEX IF NOT EXISTS idx_cache_last_hit
                ON public.rag_semantic_cache(last_hit_at DESC);
            ''')
            db.session.execute(rag_ddl)
            db.session.commit()
        except Exception as e:
            log.warning(f'Ensuring RAG/CAG tables failed: {e}')

        # ── Submission tables ─────────────────────────────────────────────────
        try:
            submission_ddl = text('''
            CREATE TABLE IF NOT EXISTS public.applications (
                id              VARCHAR(80) PRIMARY KEY,
                applicant_id    VARCHAR(80) NOT NULL,
                service_id      VARCHAR(255),
                status          VARCHAR(50) NOT NULL DEFAULT 'draft',
                data            JSONB        NOT NULL DEFAULT '{}',
                signature_type  VARCHAR(50),
                submitted_at    TIMESTAMPTZ,
                created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
                updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_app_applicant
                ON public.applications(applicant_id);
            CREATE INDEX IF NOT EXISTS idx_app_status
                ON public.applications(status);
            CREATE INDEX IF NOT EXISTS idx_app_service
                ON public.applications(service_id);

            CREATE TABLE IF NOT EXISTS public.application_documents (
                id              VARCHAR(80) PRIMARY KEY,
                application_id  VARCHAR(80) NOT NULL
                    REFERENCES public.applications(id) ON DELETE CASCADE,
                requirement_id  VARCHAR(80),
                filename        VARCHAR(255) NOT NULL,
                original_name   VARCHAR(255),
                mime_type       VARCHAR(100),
                size            BIGINT,
                storage_path    VARCHAR(500),
                processed_text  TEXT,
                created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_appdoc_app
                ON public.application_documents(application_id);

            CREATE TABLE IF NOT EXISTS public.application_status_history (
                id              SERIAL PRIMARY KEY,
                application_id  VARCHAR(80) NOT NULL
                    REFERENCES public.applications(id) ON DELETE CASCADE,
                status          VARCHAR(50) NOT NULL,
                note            TEXT,
                by              VARCHAR(80),
                created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_apphist_app
                ON public.application_status_history(application_id);

            CREATE TABLE IF NOT EXISTS public.service_requirements (
                id              VARCHAR(80) PRIMARY KEY,
                service_id      VARCHAR(255) NOT NULL,
                doc_name        VARCHAR(255) NOT NULL,
                doc_description TEXT,
                is_required     BOOLEAN NOT NULL DEFAULT TRUE,
                doc_type        VARCHAR(50) NOT NULL DEFAULT 'original',
                order_index     INTEGER NOT NULL DEFAULT 0,
                template_file   VARCHAR(255)
            );
            CREATE INDEX IF NOT EXISTS idx_req_service
                ON public.service_requirements(service_id);
            ''')
            db.session.execute(submission_ddl)
            db.session.commit()
            log.debug('Submission tables OK')
        except Exception as e:
            log.warning(f'Ensuring submission tables failed: {e}')
            db.session.rollback()

        # ── Queue tables ──────────────────────────────────────────────────────
        try:
            queue_ddl = text('''
            CREATE TABLE IF NOT EXISTS public.queue_tickets (
                id              VARCHAR(80)  PRIMARY KEY,
                agency_id       VARCHAR(120) NOT NULL,
                service_id      VARCHAR(120) NOT NULL DEFAULT '',
                service_name    VARCHAR(255) NOT NULL DEFAULT '',
                ticket_number   INTEGER      NOT NULL,
                prefix          VARCHAR(5)   NOT NULL DEFAULT 'A',
                user_id         VARCHAR(80),
                user_name       VARCHAR(255) NOT NULL DEFAULT '',
                counter_no      INTEGER,
                status          VARCHAR(30)  NOT NULL DEFAULT 'waiting',
                priority        INTEGER      NOT NULL DEFAULT 0,
                estimated_wait  INTEGER      NOT NULL DEFAULT 0,
                called_at       TIMESTAMPTZ,
                served_at       TIMESTAMPTZ,
                done_at         TIMESTAMPTZ,
                date            DATE         NOT NULL DEFAULT CURRENT_DATE,
                created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
                updated_at      TIMESTAMPTZ  NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_qt_agency_date
                ON public.queue_tickets(agency_id, date);
            CREATE INDEX IF NOT EXISTS idx_qt_user
                ON public.queue_tickets(user_id, date);
            CREATE INDEX IF NOT EXISTS idx_qt_status
                ON public.queue_tickets(status, agency_id, date);

            CREATE TABLE IF NOT EXISTS public.agency_counters (
                id              VARCHAR(80)  PRIMARY KEY,
                agency_id       VARCHAR(120) NOT NULL,
                counter_no      INTEGER      NOT NULL,
                is_active       BOOLEAN      NOT NULL DEFAULT TRUE,
                operator_name   VARCHAR(255) NOT NULL DEFAULT '',
                created_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
                updated_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
                UNIQUE (agency_id, counter_no)
            );
            CREATE INDEX IF NOT EXISTS idx_ac_agency
                ON public.agency_counters(agency_id);

            CREATE TABLE IF NOT EXISTS public.service_stats (
                agency_id       VARCHAR(120) NOT NULL,
                service_id      VARCHAR(120) NOT NULL,
                sample_count    INTEGER      NOT NULL DEFAULT 0,
                total_seconds   FLOAT        NOT NULL DEFAULT 0,
                avg_seconds     FLOAT        NOT NULL DEFAULT 420,
                updated_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
                PRIMARY KEY (agency_id, service_id)
            );
            ''')
            db.session.execute(queue_ddl)
            db.session.commit()
            log.debug('Queue tables OK')
        except Exception as e:
            log.warning(f'Ensuring queue tables failed: {e}')
            db.session.rollback()

        # ── Appointments table ────────────────────────────────────────────────
        try:
            appt_ddl = text('''
            CREATE TABLE IF NOT EXISTS public.appointments (
                id           VARCHAR(80)  PRIMARY KEY,
                user_id      VARCHAR(80),
                agency_id    VARCHAR(255) NOT NULL,
                service_code VARCHAR(100) NOT NULL,
                date         DATE         NOT NULL,
                time         VARCHAR(10)  NOT NULL,
                status       VARCHAR(30)  NOT NULL DEFAULT 'pending',
                full_name    VARCHAR(255),
                phone        VARCHAR(50),
                info         TEXT,
                queue_number INTEGER,
                created_at   TIMESTAMPTZ  NOT NULL DEFAULT now(),
                updated_at   TIMESTAMPTZ  NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_appt_user
                ON public.appointments(user_id, date);
            CREATE INDEX IF NOT EXISTS idx_appt_agency
                ON public.appointments(agency_id, date);
            CREATE INDEX IF NOT EXISTS idx_appt_status
                ON public.appointments(status, agency_id, date);
            ''')
            db.session.execute(appt_ddl)
            db.session.commit()
            log.debug('Appointments table OK')
        except Exception as e:
            log.warning(f'Ensuring appointments table failed: {e}')
            db.session.rollback()

        # ── Chatbot config tables ─────────────────────────────────────────────
        try:
            chatbot_ddl = text('''
            CREATE TABLE IF NOT EXISTS public.chatbot_personas (
                id          VARCHAR(80)  PRIMARY KEY DEFAULT gen_random_uuid()::text,
                name        VARCHAR(100) NOT NULL DEFAULT 'Trợ lý công',
                tone        VARCHAR(50)  NOT NULL DEFAULT 'formal',
                language    VARCHAR(10)  NOT NULL DEFAULT 'vi',
                greeting    TEXT         NOT NULL DEFAULT 'Xin chào! Tôi là trợ lý hành chính công. Tôi có thể giúp gì cho bạn?',
                farewell    TEXT         NOT NULL DEFAULT 'Cảm ơn bạn đã sử dụng dịch vụ. Chúc bạn một ngày tốt lành!',
                description TEXT,
                is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
                created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
                updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS public.chatbot_prompts (
                id          VARCHAR(80)  PRIMARY KEY DEFAULT gen_random_uuid()::text,
                type        VARCHAR(50)  NOT NULL,
                name        VARCHAR(150) NOT NULL,
                content     TEXT         NOT NULL,
                description TEXT,
                variables   JSONB        NOT NULL DEFAULT '[]',
                is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
                persona_id  VARCHAR(80)  REFERENCES public.chatbot_personas(id) ON DELETE SET NULL,
                created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
                updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_cprompt_type
                ON public.chatbot_prompts(type, is_active);

            CREATE TABLE IF NOT EXISTS public.chatbot_rules (
                id          VARCHAR(80)  PRIMARY KEY DEFAULT gen_random_uuid()::text,
                category    VARCHAR(80)  NOT NULL,
                rule_text   TEXT         NOT NULL,
                priority    INTEGER      NOT NULL DEFAULT 0,
                is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
                created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
                updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_crule_cat
                ON public.chatbot_rules(category, is_active, priority DESC);

            CREATE TABLE IF NOT EXISTS public.chatbot_sessions (
                id          VARCHAR(80)  PRIMARY KEY,
                user_id     VARCHAR(80),
                mode        VARCHAR(30)  NOT NULL DEFAULT 'general',
                state       JSONB        NOT NULL DEFAULT '{}',
                history     JSONB        NOT NULL DEFAULT '[]',
                created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
                updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_csess_user
                ON public.chatbot_sessions(user_id, updated_at DESC);
            ''')
            db.session.execute(chatbot_ddl)
            db.session.commit()
            log.debug('Chatbot config tables OK')
        except Exception as e:
            log.warning(f'Ensuring chatbot tables failed: {e}')
            db.session.rollback()

        # ── Evaluations + form_templates + procedures tables ─────────────────
        # QUAN TRỌNG: Phải tạo TRƯỚC khối hardening (FK constraints)
        try:
            eval_ddl = text('''
            CREATE TABLE IF NOT EXISTS public.evaluations (
                id                VARCHAR(80)  PRIMARY KEY,
                application_id    VARCHAR(80)  NOT NULL,
                user_id           VARCHAR(80)  NOT NULL,
                agency_id         VARCHAR(255) NOT NULL DEFAULT '',
                service_name      VARCHAR(255) NOT NULL DEFAULT '',
                attitude_rating   INTEGER      NOT NULL DEFAULT 0
                    CHECK (attitude_rating BETWEEN 1 AND 5),
                time_rating       INTEGER      NOT NULL DEFAULT 0
                    CHECK (time_rating BETWEEN 1 AND 5),
                facilities_rating INTEGER      NOT NULL DEFAULT 0
                    CHECK (facilities_rating BETWEEN 1 AND 5),
                avg_rating        FLOAT        NOT NULL DEFAULT 0,
                comment           TEXT         NOT NULL DEFAULT '',
                submitted_at      TIMESTAMPTZ  NOT NULL DEFAULT now(),
                created_at        TIMESTAMPTZ  NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_eval_user
                ON public.evaluations(user_id, submitted_at DESC);
            CREATE INDEX IF NOT EXISTS idx_eval_app
                ON public.evaluations(application_id);
            CREATE INDEX IF NOT EXISTS idx_eval_agency
                ON public.evaluations(agency_id, submitted_at DESC);

            CREATE TABLE IF NOT EXISTS public.form_templates (
                id                  VARCHAR(80)  PRIMARY KEY,
                name                VARCHAR(255) NOT NULL,
                description         TEXT         NOT NULL DEFAULT '',
                service_id          VARCHAR(255),
                filename            VARCHAR(255) NOT NULL,
                original_name       VARCHAR(255),
                storage_path        VARCHAR(500),
                extracted_structure JSONB        NOT NULL DEFAULT '{}',
                created_by          VARCHAR(80),
                created_at          TIMESTAMPTZ  NOT NULL DEFAULT now(),
                updated_at          TIMESTAMPTZ  NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_ft_service
                ON public.form_templates(service_id);
            CREATE INDEX IF NOT EXISTS idx_ft_created
                ON public.form_templates(created_at DESC);

            CREATE TABLE IF NOT EXISTS public.procedures (
                id                  VARCHAR(80)  PRIMARY KEY,
                name                VARCHAR(255) NOT NULL,
                code                VARCHAR(50),
                category            VARCHAR(80)  NOT NULL DEFAULT '',
                fee                 INTEGER      NOT NULL DEFAULT 0,
                fee_note            TEXT         NOT NULL DEFAULT '',
                processing_days     INTEGER      NOT NULL DEFAULT 0,
                processing_note     TEXT         NOT NULL DEFAULT '',
                legal_basis         JSONB        NOT NULL DEFAULT '[]',
                implementing_level  VARCHAR(30)  NOT NULL DEFAULT 'ward',
                agency              TEXT         NOT NULL DEFAULT '',
                is_online           BOOLEAN      NOT NULL DEFAULT TRUE,
                is_active           BOOLEAN      NOT NULL DEFAULT TRUE,
                created_at          TIMESTAMPTZ  NOT NULL DEFAULT now(),
                updated_at          TIMESTAMPTZ  NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_proc_category
                ON public.procedures(category, is_active);
            CREATE INDEX IF NOT EXISTS idx_proc_level
                ON public.procedures(implementing_level, is_active);
            CREATE INDEX IF NOT EXISTS idx_proc_active
                ON public.procedures(is_active, name);
            ''')
            db.session.execute(eval_ddl)
            db.session.commit()
            log.debug('Evaluations + form_templates + procedures tables OK')
        except Exception as e:
            log.warning(f'Ensuring evaluations/form_templates/procedures tables failed: {e}')
            db.session.rollback()

        # ── Audit log table ───────────────────────────────────────────────────
        try:
            audit_ddl = text('''
            CREATE TABLE IF NOT EXISTS public.audit_logs (
                id          BIGSERIAL    PRIMARY KEY,
                actor_id    VARCHAR(80),
                actor_role  VARCHAR(50),
                action      VARCHAR(100) NOT NULL,
                resource    VARCHAR(100) NOT NULL,
                resource_id VARCHAR(80),
                detail      JSONB        NOT NULL DEFAULT '{}',
                ip          VARCHAR(45),
                created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_audit_actor
                ON public.audit_logs(actor_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_audit_resource
                ON public.audit_logs(resource, resource_id, created_at DESC);
            CREATE INDEX IF NOT EXISTS idx_audit_created
                ON public.audit_logs(created_at DESC);
            ''')
            db.session.execute(audit_ddl)
            db.session.commit()
            log.debug('Audit log table OK')
        except Exception as e:
            log.warning(f'Ensuring audit_logs table failed: {e}')
            db.session.rollback()

        # ── Schema hardening: FK, indexes, CHECK constraints ──────────────────
        try:
            hardening_ddl = text('''
            -- Materialize applicant_name từ JSONB → column riêng để index và tìm kiếm nhanh
            ALTER TABLE public.applications
                ADD COLUMN IF NOT EXISTS applicant_name VARCHAR(255);

            -- Backfill từ JSONB data
            UPDATE public.applications
            SET applicant_name = data->>'applicantName'
            WHERE applicant_name IS NULL AND data->>'applicantName' IS NOT NULL;

            -- Index cho search theo tên (thay thế ILIKE trên JSONB)
            CREATE INDEX IF NOT EXISTS idx_app_applicant_name
                ON public.applications(applicant_name);

            -- GIN index cho tìm kiếm toàn văn trong JSONB data
            CREATE INDEX IF NOT EXISTS idx_app_data_gin
                ON public.applications USING gin(data jsonb_path_ops);

            -- Compound index cho tìm kiếm + phân quyền
            CREATE INDEX IF NOT EXISTS idx_app_applicant_status
                ON public.applications(applicant_id, status, created_at DESC);

            -- Index lịch sử trạng thái theo thời gian
            CREATE INDEX IF NOT EXISTS idx_apphist_time
                ON public.application_status_history(application_id, created_at DESC);

            -- Compound index cho hàng chờ (query chính của queue)
            CREATE INDEX IF NOT EXISTS idx_qt_agency_status_date
                ON public.queue_tickets(agency_id, status, date);

            -- Index cho lịch hẹn theo ngày + cơ quan
            CREATE INDEX IF NOT EXISTS idx_appt_agency_date_status
                ON public.appointments(agency_id, date, status);

            -- FK: applications → users (không xóa cascade vì audit cần giữ)
            ALTER TABLE public.applications
                DROP CONSTRAINT IF EXISTS fk_app_applicant;
            ALTER TABLE public.applications
                ADD CONSTRAINT fk_app_applicant
                FOREIGN KEY (applicant_id) REFERENCES public.users(id)
                ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;

            -- FK: application_documents → applications (cascade xóa khi xóa hồ sơ)
            ALTER TABLE public.application_documents
                DROP CONSTRAINT IF EXISTS fk_appdoc_app;
            ALTER TABLE public.application_documents
                ADD CONSTRAINT fk_appdoc_app
                FOREIGN KEY (application_id) REFERENCES public.applications(id)
                ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;

            -- FK: application_status_history → applications
            ALTER TABLE public.application_status_history
                DROP CONSTRAINT IF EXISTS fk_apphist_app;
            ALTER TABLE public.application_status_history
                ADD CONSTRAINT fk_apphist_app
                FOREIGN KEY (application_id) REFERENCES public.applications(id)
                ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;

            -- FK: evaluations → applications + users
            ALTER TABLE public.evaluations
                DROP CONSTRAINT IF EXISTS fk_eval_app;
            ALTER TABLE public.evaluations
                ADD CONSTRAINT fk_eval_app
                FOREIGN KEY (application_id) REFERENCES public.applications(id)
                ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;

            ALTER TABLE public.evaluations
                DROP CONSTRAINT IF EXISTS fk_eval_user;
            ALTER TABLE public.evaluations
                ADD CONSTRAINT fk_eval_user
                FOREIGN KEY (user_id) REFERENCES public.users(id)
                ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;

            -- FK: appointments → users
            ALTER TABLE public.appointments
                DROP CONSTRAINT IF EXISTS fk_appt_user;
            ALTER TABLE public.appointments
                ADD CONSTRAINT fk_appt_user
                FOREIGN KEY (user_id) REFERENCES public.users(id)
                ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;

            -- CHECK constraints trên status
            ALTER TABLE public.applications
                DROP CONSTRAINT IF EXISTS chk_app_status;
            ALTER TABLE public.applications
                ADD CONSTRAINT chk_app_status
                CHECK (status IN ('draft','submitted','in_review','approved','rejected','more_info','withdraw'));

            ALTER TABLE public.queue_tickets
                DROP CONSTRAINT IF EXISTS chk_qt_status;
            ALTER TABLE public.queue_tickets
                ADD CONSTRAINT chk_qt_status
                CHECK (status IN ('waiting','called','serving','done','absent','cancelled'));

            ALTER TABLE public.evaluations
                DROP CONSTRAINT IF EXISTS chk_eval_ratings;
            ALTER TABLE public.evaluations
                ADD CONSTRAINT chk_eval_ratings
                CHECK (
                    attitude_rating BETWEEN 1 AND 5 AND
                    time_rating     BETWEEN 1 AND 5 AND
                    facilities_rating BETWEEN 1 AND 5
                );

            -- Xóa orphan references trước khi thêm FK (tránh lỗi constraint violation)
            UPDATE public.queue_tickets
                SET user_id = NULL
                WHERE user_id IS NOT NULL
                AND user_id NOT IN (SELECT id FROM public.users);

            UPDATE public.chatbot_sessions
                SET user_id = NULL
                WHERE user_id IS NOT NULL
                AND user_id NOT IN (SELECT id FROM public.users);

            UPDATE public.audit_logs
                SET actor_id = NULL
                WHERE actor_id IS NOT NULL
                AND actor_id NOT IN (SELECT id FROM public.users);

            UPDATE public.form_templates
                SET created_by = NULL
                WHERE created_by IS NOT NULL
                AND created_by NOT IN (SELECT id FROM public.users);

            UPDATE public.application_documents
                SET requirement_id = NULL
                WHERE requirement_id IS NOT NULL
                AND requirement_id NOT IN (SELECT id FROM public.service_requirements);

            -- FK: queue_tickets → users (user_id nullable — khách lấy số không cần đăng nhập)
            ALTER TABLE public.queue_tickets
                DROP CONSTRAINT IF EXISTS fk_qt_user;
            ALTER TABLE public.queue_tickets
                ADD CONSTRAINT fk_qt_user
                FOREIGN KEY (user_id) REFERENCES public.users(id)
                ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;

            -- FK: chatbot_sessions → users (user_id nullable — session ẩn danh)
            ALTER TABLE public.chatbot_sessions
                DROP CONSTRAINT IF EXISTS fk_csess_user;
            ALTER TABLE public.chatbot_sessions
                ADD CONSTRAINT fk_csess_user
                FOREIGN KEY (user_id) REFERENCES public.users(id)
                ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;

            -- FK: audit_logs → users (actor_id nullable — system actions)
            ALTER TABLE public.audit_logs
                DROP CONSTRAINT IF EXISTS fk_audit_actor;
            ALTER TABLE public.audit_logs
                ADD CONSTRAINT fk_audit_actor
                FOREIGN KEY (actor_id) REFERENCES public.users(id)
                ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;

            -- FK: form_templates → users (created_by nullable)
            ALTER TABLE public.form_templates
                DROP CONSTRAINT IF EXISTS fk_ft_created_by;
            ALTER TABLE public.form_templates
                ADD CONSTRAINT fk_ft_created_by
                FOREIGN KEY (created_by) REFERENCES public.users(id)
                ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;

            -- FK: application_documents → service_requirements (requirement_id nullable)
            ALTER TABLE public.application_documents
                DROP CONSTRAINT IF EXISTS fk_appdoc_req;
            ALTER TABLE public.application_documents
                ADD CONSTRAINT fk_appdoc_req
                FOREIGN KEY (requirement_id) REFERENCES public.service_requirements(id)
                ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;

            ''')
            db.session.execute(hardening_ddl)
            db.session.commit()
            log.debug('Schema hardening OK')
        except Exception as e:
            log.warning(f'Schema hardening partially failed (may already exist): {e}')
            db.session.rollback()

        # NOT NULL migrations (tách riêng vì SQL cần single-quote cho default string)
        _notnull_stmts = [
            "UPDATE public.applications SET service_id = '' WHERE service_id IS NULL",
            "ALTER TABLE public.applications ALTER COLUMN service_id SET DEFAULT ''",
            "UPDATE public.appointments SET status = 'pending' WHERE status IS NULL",
            "ALTER TABLE public.appointments ALTER COLUMN status SET DEFAULT 'pending'",
            "ALTER TABLE public.appointments ALTER COLUMN status SET NOT NULL",
        ]
        for stmt in _notnull_stmts:
            try:
                db.session.execute(text(stmt))
                db.session.commit()
            except Exception:
                db.session.rollback()

        # ── Map data tables: ds_theloai + ds_dichvucong ──────────────────────
        try:
            map_ddl = text('''
            CREATE TABLE IF NOT EXISTS public.ds_theloai (
                id          VARCHAR(50)  PRIMARY KEY,
                name        VARCHAR(100) NOT NULL,
                code        VARCHAR(50)  UNIQUE,
                created_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS public.ds_dichvucong (
                id          VARCHAR(80)  PRIMARY KEY,
                name        VARCHAR(255) NOT NULL,
                description TEXT         NOT NULL DEFAULT '',
                category_id VARCHAR(50)  REFERENCES public.ds_theloai(id) ON DELETE SET NULL,
                address     TEXT         NOT NULL DEFAULT '',
                latitude    DOUBLE PRECISION,
                longitude   DOUBLE PRECISION,
                phone       VARCHAR(50)  NOT NULL DEFAULT '',
                email       VARCHAR(100) NOT NULL DEFAULT '',
                website     VARCHAR(255) NOT NULL DEFAULT '',
                level       VARCHAR(30)  NOT NULL DEFAULT 'district',
                status      VARCHAR(20)  NOT NULL DEFAULT 'normal',
                rating      FLOAT        NOT NULL DEFAULT 0,
                field       VARCHAR(255) NOT NULL DEFAULT '',
                province    VARCHAR(100) NOT NULL DEFAULT '',
                district    VARCHAR(100) NOT NULL DEFAULT '',
                ward        VARCHAR(100) NOT NULL DEFAULT '',
                created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
                updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_dv_category ON public.ds_dichvucong(category_id);
            CREATE INDEX IF NOT EXISTS idx_dv_level    ON public.ds_dichvucong(level);
            CREATE INDEX IF NOT EXISTS idx_dv_coords   ON public.ds_dichvucong(latitude, longitude)
                WHERE latitude IS NOT NULL AND longitude IS NOT NULL;
            ''')
            db.session.execute(map_ddl)
            db.session.commit()
            log.debug('Map data tables OK')
        except Exception as e:
            log.warning(f'Ensuring map tables failed: {e}')
            db.session.rollback()

        # ── Agencies table + FK constraints ──────────────────────────────────
        try:
            agencies_ddl = text('''
            CREATE TABLE IF NOT EXISTS public.agencies (
                id          VARCHAR(255) PRIMARY KEY,
                name        VARCHAR(255) NOT NULL DEFAULT '',
                address     TEXT         NOT NULL DEFAULT '',
                ward        VARCHAR(100) NOT NULL DEFAULT '',
                district    VARCHAR(100) NOT NULL DEFAULT '',
                province    VARCHAR(100) NOT NULL DEFAULT '',
                latitude    DOUBLE PRECISION,
                longitude   DOUBLE PRECISION,
                level       VARCHAR(30)  NOT NULL DEFAULT 'district',
                phone       VARCHAR(50)  NOT NULL DEFAULT '',
                email       VARCHAR(255) NOT NULL DEFAULT '',
                website     VARCHAR(255) NOT NULL DEFAULT '',
                is_active   BOOLEAN      NOT NULL DEFAULT TRUE,
                created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
                updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
            );
            CREATE INDEX IF NOT EXISTS idx_agencies_level
                ON public.agencies(level, is_active);
            CREATE INDEX IF NOT EXISTS idx_agencies_district
                ON public.agencies(district);

            -- Seed placeholder agencies từ agency_id đang tồn tại (tránh vi phạm FK)
            INSERT INTO public.agencies (id, name)
                SELECT DISTINCT agency_id, agency_id FROM public.queue_tickets
                WHERE agency_id IS NOT NULL AND agency_id <> ''
            ON CONFLICT (id) DO NOTHING;

            INSERT INTO public.agencies (id, name)
                SELECT DISTINCT agency_id, agency_id FROM public.appointments
                WHERE agency_id IS NOT NULL AND agency_id <> ''
            ON CONFLICT (id) DO NOTHING;

            INSERT INTO public.agencies (id, name)
                SELECT DISTINCT agency_id, agency_id FROM public.agency_counters
                WHERE agency_id IS NOT NULL AND agency_id <> ''
            ON CONFLICT (id) DO NOTHING;

            INSERT INTO public.agencies (id, name)
                SELECT DISTINCT agency_id, agency_id FROM public.service_stats
                WHERE agency_id IS NOT NULL AND agency_id <> ''
            ON CONFLICT (id) DO NOTHING;

            INSERT INTO public.agencies (id, name)
                SELECT DISTINCT agency_id, agency_id FROM public.agency_queue_realtime
                WHERE agency_id IS NOT NULL AND agency_id <> ''
            ON CONFLICT (id) DO NOTHING;

            -- evaluations.agency_id có thể là '' (empty) → đổi sang nullable trước khi add FK
            ALTER TABLE public.evaluations
                ALTER COLUMN agency_id DROP NOT NULL;
            UPDATE public.evaluations
                SET agency_id = NULL WHERE agency_id = '';

            INSERT INTO public.agencies (id, name)
                SELECT DISTINCT agency_id, agency_id FROM public.evaluations
                WHERE agency_id IS NOT NULL AND agency_id <> ''
            ON CONFLICT (id) DO NOTHING;

            -- FK: queue_tickets → agencies (RESTRICT — không xóa cơ quan đang có vé)
            ALTER TABLE public.queue_tickets
                DROP CONSTRAINT IF EXISTS fk_qt_agency;
            ALTER TABLE public.queue_tickets
                ADD CONSTRAINT fk_qt_agency
                FOREIGN KEY (agency_id) REFERENCES public.agencies(id)
                ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;

            -- FK: appointments → agencies
            ALTER TABLE public.appointments
                DROP CONSTRAINT IF EXISTS fk_appt_agency;
            ALTER TABLE public.appointments
                ADD CONSTRAINT fk_appt_agency
                FOREIGN KEY (agency_id) REFERENCES public.agencies(id)
                ON DELETE RESTRICT DEFERRABLE INITIALLY DEFERRED;

            -- FK: evaluations → agencies (SET NULL vì nullable)
            ALTER TABLE public.evaluations
                DROP CONSTRAINT IF EXISTS fk_eval_agency;
            ALTER TABLE public.evaluations
                ADD CONSTRAINT fk_eval_agency
                FOREIGN KEY (agency_id) REFERENCES public.agencies(id)
                ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;

            -- FK: agency_queue_realtime → agencies (CASCADE — xóa snapshot khi xóa cơ quan)
            ALTER TABLE public.agency_queue_realtime
                DROP CONSTRAINT IF EXISTS fk_aqr_agency;
            ALTER TABLE public.agency_queue_realtime
                ADD CONSTRAINT fk_aqr_agency
                FOREIGN KEY (agency_id) REFERENCES public.agencies(id)
                ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;

            -- FK: agency_counters → agencies
            ALTER TABLE public.agency_counters
                DROP CONSTRAINT IF EXISTS fk_ac_agency;
            ALTER TABLE public.agency_counters
                ADD CONSTRAINT fk_ac_agency
                FOREIGN KEY (agency_id) REFERENCES public.agencies(id)
                ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;

            -- FK: service_stats → agencies
            ALTER TABLE public.service_stats
                DROP CONSTRAINT IF EXISTS fk_ss_agency;
            ALTER TABLE public.service_stats
                ADD CONSTRAINT fk_ss_agency
                FOREIGN KEY (agency_id) REFERENCES public.agencies(id)
                ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED;
            ''')
            db.session.execute(agencies_ddl)
            db.session.commit()
            log.debug('Agencies table + FK OK')
        except Exception as e:
            log.warning(f'Ensuring agencies table/FK failed: {e}')
            db.session.rollback()

        # ── Remaining FK constraints ──────────────────────────────────────────
        try:
            remaining_ddl = text('''
            -- 1. Thêm user_id vào chat_sessions (RAG) để liên kết phiên với tài khoản
            ALTER TABLE public.chat_sessions
                ADD COLUMN IF NOT EXISTS user_id VARCHAR(80);
            CREATE INDEX IF NOT EXISTS idx_chat_sess_user
                ON public.chat_sessions(user_id);

            UPDATE public.chat_sessions
                SET user_id = NULL
                WHERE user_id IS NOT NULL
                AND user_id NOT IN (SELECT id FROM public.users);

            ALTER TABLE public.chat_sessions
                DROP CONSTRAINT IF EXISTS fk_chat_sess_user;
            ALTER TABLE public.chat_sessions
                ADD CONSTRAINT fk_chat_sess_user
                FOREIGN KEY (user_id) REFERENCES public.users(id)
                ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;

            -- 2. application_status_history.by → users (ai thay đổi trạng thái hồ sơ)
            UPDATE public.application_status_history
                SET by = NULL
                WHERE by IS NOT NULL
                AND by NOT IN (SELECT id FROM public.users);

            ALTER TABLE public.application_status_history
                DROP CONSTRAINT IF EXISTS fk_apphist_by;
            ALTER TABLE public.application_status_history
                ADD CONSTRAINT fk_apphist_by
                FOREIGN KEY (by) REFERENCES public.users(id)
                ON DELETE SET NULL DEFERRABLE INITIALLY DEFERRED;

            -- 3. procedures.code → thêm UNIQUE để appointments.service_code có thể tham chiếu
            -- Xử lý duplicate code trước: giữ lại bản ghi mới nhất
            UPDATE public.procedures p
                SET code = id
                WHERE code IS NOT NULL
                AND (
                    SELECT COUNT(*) FROM public.procedures p2
                    WHERE p2.code = p.code AND p2.id <> p.id
                ) > 0;

            -- Xử lý code NULL → dùng id làm code
            UPDATE public.procedures
                SET code = id
                WHERE code IS NULL OR code = '';

            ALTER TABLE public.procedures
                DROP CONSTRAINT IF EXISTS uq_procedures_code;
            ALTER TABLE public.procedures
                ADD CONSTRAINT uq_procedures_code UNIQUE (code);

            ''')
            db.session.execute(remaining_ddl)
            db.session.commit()
            log.debug('Remaining FK constraints OK')
        except Exception as e:
            log.warning(f'Remaining FK constraints partially failed: {e}')
            db.session.rollback()

        # ── System settings table ─────────────────────────────────────────────
        try:
            settings_ddl = text('''
            CREATE TABLE IF NOT EXISTS public.system_settings (
                key         VARCHAR(100) PRIMARY KEY,
                value       TEXT         NOT NULL DEFAULT '',
                type        VARCHAR(20)  NOT NULL DEFAULT 'string',
                label       VARCHAR(255) NOT NULL DEFAULT '',
                description TEXT         NOT NULL DEFAULT '',
                updated_by  VARCHAR(80),
                updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
            );

            -- Seed giá trị mặc định nếu chưa có
            INSERT INTO public.system_settings (key, value, type, label, description) VALUES
                ('enableChatbot',       'true',  'bool',   'Trợ lý Chatbot AI',         'Bật/tắt chatbot trên toàn ứng dụng')
               ,('enableQueue',         'true',  'bool',   'Hàng đợi trực tuyến',        'Cho phép lấy số thứ tự qua app')
               ,('enableVoice',         'false', 'bool',   'Đặt lịch bằng giọng nói',    'Tính năng Voice AI cho đặt lịch')
               ,('enableNotifications', 'true',  'bool',   'Push notification',           'Gửi thông báo đẩy đến người dùng')
               ,('maintenanceMode',     'false', 'bool',   'Chế độ bảo trì',             'Tạm dừng ứng dụng cho người dùng thường')
               ,('debugMode',           'false', 'bool',   'Debug mode',                  'In log chi tiết ra console')
               ,('announcementActive',  'false', 'bool',   'Banner thông báo',            'Hiện banner ở trang chủ')
               ,('announcementText',    '',      'string', 'Nội dung thông báo',          'Nội dung hiện trong banner trang chủ')
               ,('announcementType',    'info',  'string', 'Loại thông báo',              'info | warning | error | success')
               ,('appName',             'E-Mapp Dịch vụ công', 'string', 'Tên ứng dụng', 'Tên hiển thị của ứng dụng')
               ,('contactEmail',        '',      'string', 'Email liên hệ',               'Email hỗ trợ người dùng')
               ,('contactPhone',        '',      'string', 'Hotline',                     'Số điện thoại hỗ trợ')
               ,('contactAddress',      '',      'string', 'Địa chỉ',                     'Địa chỉ cơ quan chủ quản')
            ON CONFLICT (key) DO NOTHING;
            ''')
            db.session.execute(settings_ddl)
            db.session.commit()
            log.debug('System settings table OK')
        except Exception as e:
            log.warning(f'Ensuring system_settings table failed: {e}')
            db.session.rollback()

        # ── Thêm admin_reply vào evaluations (nếu chưa có) ──────────────────
        try:
            db.session.execute(text('''
                ALTER TABLE public.evaluations
                    ADD COLUMN IF NOT EXISTS admin_reply       TEXT         DEFAULT NULL,
                    ADD COLUMN IF NOT EXISTS admin_replied_at  TIMESTAMPTZ  DEFAULT NULL,
                    ADD COLUMN IF NOT EXISTS admin_id          VARCHAR(80)  DEFAULT NULL;
            '''))
            db.session.commit()
            log.debug('evaluations admin_reply columns OK')
        except Exception as e:
            log.warning(f'evaluations admin_reply migration failed: {e}')
            db.session.rollback()

        # ── Migrate service_requirements — thêm template_file nếu chưa có ────────
        try:
            db.session.execute(text('''
                ALTER TABLE public.service_requirements
                    ADD COLUMN IF NOT EXISTS template_file VARCHAR(255);
            '''))
            db.session.commit()
            log.debug('service_requirements template_file migration OK')
        except Exception as e:
            log.warning(f'service_requirements template_file migration failed: {e}')
            db.session.rollback()

        # ── Xóa FK service-related bị add nhầm (service_code/service_id dùng keyword tự do)
        _drop_wrong_fks = [
            "ALTER TABLE public.appointments DROP CONSTRAINT IF EXISTS fk_appt_service",
            "ALTER TABLE public.service_requirements DROP CONSTRAINT IF EXISTS fk_req_procedure",
            "ALTER TABLE public.form_templates DROP CONSTRAINT IF EXISTS fk_ft_procedure",
            "ALTER TABLE public.queue_tickets DROP CONSTRAINT IF EXISTS fk_qt_service",
            "ALTER TABLE public.service_stats DROP CONSTRAINT IF EXISTS fk_ss_service",
        ]
        for stmt in _drop_wrong_fks:
            try:
                db.session.execute(text(stmt))
                db.session.commit()
            except Exception:
                db.session.rollback()

    return db


def test_connection():
    """Test database connection"""
    try:
        from sqlalchemy import text
        result = db.session.execute(text('SELECT 1'))
        return result.fetchone() is not None
    except Exception as e:
        log.error(f"Database connection failed: {e}")
        return False
