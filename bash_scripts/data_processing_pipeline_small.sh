BASE_DIR="/home/dom_dillingham/finalproject/HurtfulWords"
OUTPUT_DIR="/home/dom_dillingham/finalproject/HurtfulWords/data"
mkdir -p "$OUTPUT_DIR/finetuning"
SCIBERT_DIR="/home/dom_dillingham/finalproject/scibert/scibert_scivocab_uncased"
MIMIC_BENCHMARK_DIR="/home/dom_dillingham/finalproject/mimic3-benchmarks/data"

cd "$BASE_DIR/scripts/"

echo "Processing MIMIC data..."
python get_data.py $OUTPUT_DIR

echo "Tokenizing sentences..."
python sentence_tokenization.py "$OUTPUT_DIR/df_raw.pkl" "$OUTPUT_DIR/df_extract.pkl" "$SCIBERT_DIR"
rm "$OUTPUT_DIR/df_raw.pkl"

echo "Generating finetuning targets..."
python make_targets_small.py \
	--processed_df "$OUTPUT_DIR/df_extract.pkl" \
	--mimic_benchmark_dir "$MIMIC_BENCHMARK_DIR" \
	--output_dir "$OUTPUT_DIR/finetuning/"
