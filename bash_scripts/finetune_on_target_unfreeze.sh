# $1 - target type {inhosp_mort, phenotype_first, phenotype_all}
# $2 - BERT model name {baseline_clinical_BERT_1_epoch_512, adv_clinical_BERT_1_epoch_512}
# $3 - target column name within the dataframe, ex: "Shock", "any_acute"

set -e
source activate hurtfulwords

BASE_DIR="/home/dom_dillingham/finalproject/HurtfulWords"
OUTPUT_DIR="/home/dom_dillingham/finalproject/HurtfulWords/data"

cd "$BASE_DIR/scripts"

python finetune_w_emb.py \
	--df_path "${OUTPUT_DIR}/finetuning/$1" \
	--model_path "${OUTPUT_DIR}/models/$2" \
	--fold_id 9 10\
	--target_col_name "$3" \
	--output_dir "${OUTPUT_DIR}/models/finetuned/${1}_${2}_${3}/" \
	--freeze_bert \
	--train_batch_size 32 \
	--pregen_emb_path "${OUTPUT_DIR}/pregen_embs/pregen_${2}_cat4_${1}" \
	--task_type binary \
	--other_fields age SOFA sapsii_prob sapsii_prob oasis oasis_PROB \
        --gridsearch_classifier \
        --gridsearch_c \
        --emb_method cat4
