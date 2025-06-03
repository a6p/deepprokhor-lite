import pandas as pd
from datasets import Dataset, ClassLabel
from transformers import AutoTokenizer, AutoModelForSequenceClassification, Trainer, TrainingArguments
import numpy as np
import torch

#"DeepPavlov/rubert-base-cased"

#cointegrated/rubert-tiny (10x быстрее, 10x меньше)

#cointegrated/rubert-tiny2 — самая лёгкая BERT-модель??

MODEL_NAME = "cointegrated/rubert-tiny"
NUM_LABELS = 13  # число интентов, смотри в data.csv

# Загрузка данных
df = pd.read_csv("data.csv")

# Преобразование меток в индексы
labels = list(df["label"].unique())
label2id = {l: i for i, l in enumerate(labels)}
id2label = {i: l for l, i in label2id.items()}

df["label_id"] = df["label"].map(label2id)

# Создаем датасет
dataset = Dataset.from_pandas(df)

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def preprocess_function(examples):
    return tokenizer(examples["text"], truncation=True, padding="max_length", max_length=64)

dataset = dataset.map(preprocess_function, batched=True)

# Указываем столбцы, которые будут входом модели
dataset = dataset.rename_column("label_id", "labels")
dataset.set_format(type='torch', columns=['input_ids', 'attention_mask', 'labels'])

# Разбиваем на train и eval
split = dataset.train_test_split(test_size=0.2, seed=42)
train_dataset = split["train"]
eval_dataset = split["test"]

model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME, num_labels=len(labels))

training_args = TrainingArguments(
    output_dir="./finetuned_model",
    evaluation_strategy="epoch",
    save_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=100,
    weight_decay=0.01,
    save_total_limit=2,
    load_best_model_at_end=True,
    metric_for_best_model="accuracy"
)

from sklearn.metrics import accuracy_score, precision_recall_fscore_support

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    precision, recall, f1, _ = precision_recall_fscore_support(labels, preds, average="weighted")
    acc = accuracy_score(labels, preds)
    return {
        "accuracy": acc,
        "f1": f1,
        "precision": precision,
        "recall": recall
    }

trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    compute_metrics=compute_metrics
)

trainer.train()

trainer.save_model("./finetuned_model")
tokenizer.save_pretrained("./finetuned_model")

print("Модель сохранена в ./finetuned_model")

