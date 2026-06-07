import shutil
import random
from pathlib import Path

BASE_DIR = Path(__file__).parent
RAW_DIR = BASE_DIR / "data" / "raw_data"
SPLIT_DIR = BASE_DIR / "data"

TRAIN_SAMPLE_SIZE = 1000
VAL_SAMPLE_SIZE = 200
TOTAL_SAMPLE_SIZE = TRAIN_SAMPLE_SIZE + VAL_SAMPLE_SIZE

RANDOM_SEED = 42

def split_data():
    images_train_dir = SPLIT_DIR / 'images' / 'train'
    images_val_dir = SPLIT_DIR / 'images' / 'val'
    labels_train_dir = SPLIT_DIR / 'labels' / 'train'
    labels_val_dir = SPLIT_DIR / 'labels' / 'val'

    if images_train_dir.exists():
        # 폴더 내에 jpg 파일이 있는지 확인 (next를 사용해 하나라도 찾으면 즉시 중단하여 속도 최적화)
        if next(images_train_dir.glob('*.jpg'), None) is not None:
            print("INFO: 이미 분할된 데이터가 존재하여 복사 과정을 생략합니다.")
            return
        
    all_images = []
    all_images.extend(RAW_DIR.rglob('*.jpg'))

    if not all_images:
        print(f"ERROR: 원본 이미지를 찾을 수 없습니다. | RAW_DIR={RAW_DIR}")
        return

    valid_data = []
    for img_path in all_images:
        label_path = RAW_DIR / "labels" / f"{img_path.stem}.txt"

        if label_path.exists():
            valid_data.append((img_path, label_path))

    random.seed(RANDOM_SEED)

    sampled_data = random.sample(valid_data, TOTAL_SAMPLE_SIZE)

    train_data = sampled_data[:TRAIN_SAMPLE_SIZE]
    val_data = sampled_data[TRAIN_SAMPLE_SIZE:]

    print(f"INFO: 데이터 분할 완료 | train={len(train_data)}, val={len(val_data)}")

    # 저장 폴더 생성
    for d in [images_train_dir, images_val_dir, labels_train_dir, labels_val_dir]:
        if d.exists():
            shutil.rmtree(d)
        d.mkdir(parents=True, exist_ok=True)

    # 복사
    for img, lbl in train_data:
        shutil.copy2(img, images_train_dir / img.name)
        shutil.copy2(lbl, labels_train_dir / lbl.name)
        
    for img, lbl in val_data:
        shutil.copy2(img, images_val_dir / img.name)
        shutil.copy2(lbl, labels_val_dir / lbl.name)

    print("INFO: 모든 데이터가 복사되었습니다.")