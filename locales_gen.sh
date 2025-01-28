#!/usr/bin/bash

# Параметры
INPUT_DIR="./po"
OUTPUT_DIR="./locale"

if [[ ! -d "$INPUT_DIR" ]]; then
  echo "Ошибка: Директория $INPUT_DIR не существует."
  exit 1
fi

mkdir -p "$OUTPUT_DIR"

for po_file in "$INPUT_DIR"/*.po; do
  if [[ -f "$po_file" ]]; then
    lang_code=$(basename "$po_file" .po)

    lang_dir="$OUTPUT_DIR/$lang_code/LC_MESSAGES"
    
    mkdir -p "$lang_dir"

    msgfmt "$po_file" -o "$lang_dir/messages.mo"

    echo "Создан перевод для '$lang_code' в '$lang_dir/messages.mo'"
  else
    echo "Файл $po_file не найден."
  fi
done

echo "Генерация завершена."
