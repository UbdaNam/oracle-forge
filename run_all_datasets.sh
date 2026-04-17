#!/bin/bash
cd ~/DataAgentBench && source .venv/bin/activate

LLM='google/gemini-3.1-pro-preview'
ITER=20
HARNESS=~/oracle-forge/eval/harness.py

TOTAL_PASS=0
TOTAL_ALL=0

run_dataset() {
  local dataset=$1
  local queries=$2
  echo ''
  echo '========================================'
  echo "Dataset: $dataset | Queries: $queries"
  echo '========================================'
  result=$(python3 $HARNESS --dataset $dataset --queries $queries --llm $LLM --iterations $ITER 2>&1)
  echo "$result" | grep -E 'PASS|FAIL|SCORE|self-correct'
  score_line=$(echo "$result" | grep 'SCORE:')
  pass=$(echo "$score_line" | grep -oP '\d+(?=/)' | head -1)
  total=$(echo "$score_line" | grep -oP '(?<=/)\d+' | head -1)
  TOTAL_PASS=$((TOTAL_PASS + ${pass:-0}))
  TOTAL_ALL=$((TOTAL_ALL + ${total:-0}))
}

run_dataset yelp            '1,2,3,4,5,6,7'
run_dataset bookreview       '1,2,3'
run_dataset agnews           '1,2,3,4'
run_dataset googlelocal      '1,2,3,4'
run_dataset stockmarket      '1,2,3,4,5'
run_dataset stockindex       '1,2,3'
run_dataset DEPS_DEV_V1      '1,2'
run_dataset GITHUB_REPOS     '1,2,3,4'
run_dataset music_brainz_20k '1,2,3'
run_dataset PANCANCER_ATLAS  '1,2,3'
run_dataset PATENTS          '1,2,3'
run_dataset crmarenapro      '1,2,3,4,5,6,7,8,9,10,11,12,13'

echo ''
echo '========================================'
echo "FINAL: $TOTAL_PASS/$TOTAL_ALL queries passed"
python3 -c "import sys; p,t=$TOTAL_PASS,$TOTAL_ALL; print(f'pass@1 = {round(p/t*100,1)}%') if t else print('no results')"
echo '========================================'
