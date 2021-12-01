set -e
source activate hurtfulwords

BASE_DIR="/home/dom_dillingham/HurtfulWords"
OUTPUT_DIR="/home/dom_dillingham/HurtfulWords/data"
cd "$BASE_DIR/scripts"

python analyze_results.py \
	--models_path "${OUTPUT_DIR}/models/finetuned/" \
	--set_to_use "test" \
	--bootstrap \
