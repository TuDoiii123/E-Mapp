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
                order_index     INTEGER NOT NULL DEFAULT 0
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
                CHECK (status IN (''draft'',''submitted'',''in_review'',''approved'',''rejected'',''more_info'',''withdraw''));

            ALTER TABLE public.queue_tickets
                DROP CONSTRAINT IF EXISTS chk_qt_status;
            ALTER TABLE public.queue_tickets
                ADD CONSTRAINT chk_qt_status
                CHECK (status IN (''waiting'',''called'',''serving'',''done'',''absent'',''cancelled''));

            ALTER TABLE public.evaluations
                DROP CONSTRAINT IF EXISTS chk_eval_ratings;
            ALTER TABLE public.evaluations
                ADD CONSTRAINT chk_eval_ratings
                CHECK (
                    attitude_rating BETWEEN 1 AND 5 AND
                    time_rating     BETWEEN 1 AND 5 AND
                    facilities_rating BETWEEN 1 AND 5
                );

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
