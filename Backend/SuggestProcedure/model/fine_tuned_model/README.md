---
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- dense
- generated_from_trainer
- dataset_size:3579
- loss:MultipleNegativesRankingLoss
base_model: bkai-foundation-models/vietnamese-bi-encoder
widget:
- source_sentence: Tôi muốn thực hiện thủ tục tàu thuyền có trọng tải từ 200 tấn trở
    xuống, mang cờ quốc tịch của quốc gia có chung đường biên giới với việt nam nhập
    cảnh, xuất cảnh tại khu vực biên giới của việt nam và quốc gia đó thì cần chuẩn
    bị giấy tờ gì?
  sentences:
  - Cấp giấy phép khai thác tận thu khoáng sản
  - Phê duyệt phương án phá dỡ tàu biển
  - Đăng ký tập sự lại hành nghề công chứng sau khi chấm dứt tập sự hành nghề công
    chứng
- source_sentence: Thủ tục công nhận điều lệ (sửa đổi, bổ sung) quỹ; đổi tên quỹ được
    thực hiện như thế nào?
  sentences:
  - Công bố thông báo hàng hải về khu vực thi công công trình trên biển hoặc trên
    luồng hàng hải
  - Cho phép hội hoạt động trở lại sau khi bị đình chỉ có thời hạn
  - Xác nhận kết quả khảo sát, đánh giá thông tin chung đối với khoáng sản nhóm IV.
- source_sentence: Trong lĩnh vực giáo dục trung học, hướng dẫn chi tiết thủ tục sáp
    nhập, chia, tách trường trung học cơ sở, trường phổ thông có nhiều cấp học có
    cấp học cao nhất là trung học cơ sở là gì?
  sentences:
  - Chấp thuận thăm dò khoáng sản tại khu vực cấm hoạt động khoáng sản, khu vực tạm
    thời cấm hoạt động khoáng sản đối với khoáng sản nhóm II, nhóm III và nhóm IV
  - Sáp nhập, chia, tách trường trung học cơ sở, trường phổ thông có nhiều cấp học
    có cấp học cao nhất là trung học cơ sở
  - Gia hạn giấy phép khai thác khoáng sản nhóm IV.
- source_sentence: Trong lĩnh vực địa chất và khoáng sản, hướng dẫn chi tiết thủ
    tục điều chỉnh nội dung đề án đóng cửa mỏ khoáng sản đã được phê duyệt là gì?
  sentences:
  - Trả lại giấy phép khai thác khoáng sản.
  - Thanh toán chi phí khám bệnh, chữa bệnh giữa cơ quan bảo hiểm xã hội và cơ sở
    khám bệnh, chữa bệnh
  - Cấp Giấy chứng nhận xuất xứ hàng hoá (C/O) không ưu đãi mẫu B
- source_sentence: Thủ tục đề xuất cơ chế ưu đãi đầu tư theo quy định tại điểm c khoản
    2 điều 198 của luật nhà ở 2023 được thực hiện như thế nào?
  sentences:
  - Thủ tục chấp thuận chủ trương đầu tư đồng thời giao chủ đầu tư đối với trường
    hợp dự án đầu tư xây dựng nhà ở xã hội chưa được chấp thuận chủ trương đầu tư,
    chấp thuận đầu tư hoặc chưa có văn bản pháp lý tương đương
  - Thẩm định nhiệm vụ quy hoạch, nhiệm vụ điều chỉnh quy hoạch đô thị và nông thôn
    do nhà đầu tư đã được lựa chọn để thực hiện dự án đầu tư tổ chức lập
  - Gia hạn giấy phép khai thác khoáng sản.
pipeline_tag: sentence-similarity
library_name: sentence-transformers
---

# SentenceTransformer based on bkai-foundation-models/vietnamese-bi-encoder

This is a [sentence-transformers](https://www.SBERT.net) model finetuned from [bkai-foundation-models/vietnamese-bi-encoder](https://huggingface.co/bkai-foundation-models/vietnamese-bi-encoder). It maps sentences & paragraphs to a 768-dimensional dense vector space and can be used for semantic textual similarity, semantic search, paraphrase mining, text classification, clustering, and more.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
- **Base model:** [bkai-foundation-models/vietnamese-bi-encoder](https://huggingface.co/bkai-foundation-models/vietnamese-bi-encoder) <!-- at revision 84f9d9ada0d1a3c37557398b9ae9fcedcdf40be0 -->
- **Maximum Sequence Length:** 256 tokens
- **Output Dimensionality:** 768 dimensions
- **Similarity Function:** Cosine Similarity
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Sentence Transformers on Hugging Face](https://huggingface.co/models?library=sentence-transformers)

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'max_seq_length': 256, 'do_lower_case': False, 'architecture': 'RobertaModel'})
  (1): Pooling({'word_embedding_dimension': 768, 'pooling_mode_cls_token': False, 'pooling_mode_mean_tokens': True, 'pooling_mode_max_tokens': False, 'pooling_mode_mean_sqrt_len_tokens': False, 'pooling_mode_weightedmean_tokens': False, 'pooling_mode_lasttoken': False, 'include_prompt': True})
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
model = SentenceTransformer("sentence_transformers_model_id")
# Run inference
sentences = [
    'Thủ tục đề xuất cơ chế ưu đãi đầu tư theo quy định tại điểm c khoản 2 điều 198 của luật nhà ở 2023 được thực hiện như thế nào?',
    'Thủ tục chấp thuận chủ trương đầu tư đồng thời giao chủ đầu tư đối với trường hợp dự án đầu tư xây dựng nhà ở xã hội chưa được chấp thuận chủ trương đầu tư, chấp thuận đầu tư hoặc chưa có văn bản pháp lý tương đương',
    'Gia hạn giấy phép khai thác khoáng sản.',
]
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 768]

# Get the similarity scores for the embeddings
similarities = model.similarity(embeddings, embeddings)
print(similarities)
# tensor([[1.0000, 0.7989, 0.0979],
#         [0.7989, 1.0000, 0.0415],
#         [0.0979, 0.0415, 1.0000]])
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 3,579 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 1000 samples:
  |         | sentence_0                                                                          | sentence_1                                                                         | label                                                          |
  |:--------|:------------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type    | string                                                                              | string                                                                             | float                                                          |
  | details | <ul><li>min: 16 tokens</li><li>mean: 42.13 tokens</li><li>max: 177 tokens</li></ul> | <ul><li>min: 5 tokens</li><li>mean: 25.41 tokens</li><li>max: 154 tokens</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.52</li><li>max: 2.0</li></ul> |
* Samples:
  | sentence_0                                                                                                                                        | sentence_1                                                                                        | label            |
  |:--------------------------------------------------------------------------------------------------------------------------------------------------|:--------------------------------------------------------------------------------------------------|:-----------------|
  | <code>Tôi muốn thực hiện thủ tục đăng ký xét tuyển trình độ đại học, trình độ cao đẳng ngành giáo dục mầm non thì cần chuẩn bị giấy tờ gì?</code> | <code>Đăng ký xét tuyển trình độ đại học, trình độ cao đẳng ngành giáo dục mầm non</code>         | <code>2.0</code> |
  | <code>Trong lĩnh vực mỹ phẩm, hướng dẫn chi tiết thủ tục xác nhận đơn hàng nhập khẩu mỹ phẩm dùng cho nghiên cứu, kiểm nghiệm là gì?</code>       | <code>Xác nhận Đơn hàng nhập khẩu mỹ phẩm dùng cho nghiên cứu, kiểm nghiệm</code>                 | <code>2.0</code> |
  | <code>Thủ tục cấp giấy chứng nhận xuất xứ hàng hoá (c/o) ưu đãi mẫu x được thực hiện như thế nào?</code>                                          | <code>Đăng ký Giấy chứng nhận hạn ngạch thuế quan xuất khẩu mật ong tự nhiên sang Nhật Bản</code> | <code>0.0</code> |
* Loss: [<code>MultipleNegativesRankingLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#multiplenegativesrankingloss) with these parameters:
  ```json
  {
      "scale": 20.0,
      "similarity_fct": "cos_sim",
      "gather_across_devices": false
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 32
- `per_device_eval_batch_size`: 32
- `num_train_epochs`: 10
- `multi_dataset_batch_sampler`: round_robin

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `overwrite_output_dir`: False
- `do_predict`: False
- `eval_strategy`: no
- `prediction_loss_only`: True
- `per_device_train_batch_size`: 32
- `per_device_eval_batch_size`: 32
- `per_gpu_train_batch_size`: None
- `per_gpu_eval_batch_size`: None
- `gradient_accumulation_steps`: 1
- `eval_accumulation_steps`: None
- `torch_empty_cache_steps`: None
- `learning_rate`: 5e-05
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `max_grad_norm`: 1
- `num_train_epochs`: 10
- `max_steps`: -1
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: {}
- `warmup_ratio`: 0.0
- `warmup_steps`: 0
- `log_level`: passive
- `log_level_replica`: warning
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `save_safetensors`: True
- `save_on_each_node`: False
- `save_only_model`: False
- `restore_callback_states_from_checkpoint`: False
- `no_cuda`: False
- `use_cpu`: False
- `use_mps_device`: False
- `seed`: 42
- `data_seed`: None
- `jit_mode_eval`: False
- `bf16`: False
- `fp16`: False
- `fp16_opt_level`: O1
- `half_precision_backend`: auto
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `local_rank`: 0
- `ddp_backend`: None
- `tpu_num_cores`: None
- `tpu_metrics_debug`: False
- `debug`: []
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_prefetch_factor`: None
- `past_index`: -1
- `disable_tqdm`: False
- `remove_unused_columns`: True
- `label_names`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `fsdp`: []
- `fsdp_min_num_params`: 0
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `fsdp_transformer_layer_cls_to_wrap`: None
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `deepspeed`: None
- `label_smoothing_factor`: 0.0
- `optim`: adamw_torch_fused
- `optim_args`: None
- `adafactor`: False
- `group_by_length`: False
- `length_column_name`: length
- `project`: huggingface
- `trackio_space_id`: trackio
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `skip_memory_metrics`: True
- `use_legacy_prediction_loop`: False
- `push_to_hub`: False
- `resume_from_checkpoint`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_private_repo`: None
- `hub_always_push`: False
- `hub_revision`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `include_inputs_for_metrics`: False
- `include_for_metrics`: []
- `eval_do_concat_batches`: True
- `fp16_backend`: auto
- `push_to_hub_model_id`: None
- `push_to_hub_organization`: None
- `mp_parameters`: 
- `auto_find_batch_size`: False
- `full_determinism`: False
- `torchdynamo`: None
- `ray_scope`: last
- `ddp_timeout`: 1800
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `include_tokens_per_second`: False
- `include_num_input_tokens_seen`: no
- `neftune_noise_alpha`: None
- `optim_target_modules`: None
- `batch_eval_metrics`: False
- `eval_on_start`: False
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `eval_use_gather_object`: False
- `average_tokens_across_devices`: True
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: round_robin
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Logs
| Epoch  | Step | Training Loss |
|:------:|:----:|:-------------:|
| 4.4643 | 500  | 0.9698        |
| 8.9286 | 1000 | 0.7055        |


### Framework Versions
- Python: 3.12.12
- Sentence Transformers: 5.1.2
- Transformers: 4.57.1
- PyTorch: 2.9.0+cu126
- Accelerate: 1.11.0
- Datasets: 4.0.0
- Tokenizers: 0.22.1

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

#### MultipleNegativesRankingLoss
```bibtex
@misc{henderson2017efficient,
    title={Efficient Natural Language Response Suggestion for Smart Reply},
    author={Matthew Henderson and Rami Al-Rfou and Brian Strope and Yun-hsuan Sung and Laszlo Lukacs and Ruiqi Guo and Sanjiv Kumar and Balint Miklos and Ray Kurzweil},
    year={2017},
    eprint={1705.00652},
    archivePrefix={arXiv},
    primaryClass={cs.CL}
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->