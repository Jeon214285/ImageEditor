import shutil
import random
from pathlib import Path

# BASE_DIR = Path(__file__).parent
BASE_DIR = "C:/Users/214285/Desktop/ImageEditor/ml"
RAW_DIR = BASE_DIR / "data" / "raw_data"
SPLIT_DIR = BASE_DIR / "data"

TRAIN_SAMPLE_SIZE = 1000
VAL_SAMPLE_SIZE = 200
TOTAL_SAMPLE_SIZE = TRAIN_SAMPLE_SIZE + VAL_SAMPLE_SIZE

RANDOM_SEED = 42

def split_data():
    for data_dir in ['face_data', 'plate_data']:
        images_train_dir = SPLIT_DIR / data_dir / 'images' / 'train'
        images_val_dir = SPLIT_DIR / data_dir / 'images' / 'val'
        labels_train_dir = SPLIT_DIR / data_dir / 'labels' / 'train'
        labels_val_dir = SPLIT_DIR / data_dir / 'labels' / 'val'
        images_raw_dir = RAW_DIR / data_dir / 'images'
        labels_raw_dir = RAW_DIR / data_dir / 'labels'

        if images_train_dir.exists():
            # 폴더 내에 jpg 파일이 있는지 확인 (next를 사용해 하나라도 찾으면 즉시 중단하여 속도 최적화)
            if next(images_train_dir.glob('*.jpg'), None) is not None:
                print("INFO: 이미 분할된 데이터가 존재하여 복사 과정을 생략합니다.")
                continue
        
        if data_dir == 'face_data':
            all_images = []
            all_images.extend(images_raw_dir.rglob('*.jpg'))

            if not all_images:
                print(f"ERROR: 원본 이미지를 찾을 수 없습니다. | RAW_DIR={RAW_DIR / data_dir}")
                continue

            valid_data = []
            for img_path in all_images:
                label_path = labels_raw_dir / f"{img_path.stem}.txt"

                if label_path.exists():
                    valid_data.append((img_path, label_path))

            random.seed(RANDOM_SEED)

            sampled_data = random.sample(valid_data, TOTAL_SAMPLE_SIZE)

            train_data = sampled_data[:TRAIN_SAMPLE_SIZE]
            val_data = sampled_data[TRAIN_SAMPLE_SIZE:]

            print(f"INFO: [face_data] 데이터 샘플링 완료 | train={len(train_data)}, val={len(val_data)}")

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

            print("INFO: [face_data] 모든 데이터가 복사되었습니다.")

        elif data_dir == 'plate_data':
            images_train_raw_dir = images_raw_dir / 'train'
            labels_train_raw_dir = labels_raw_dir / 'train'
            images_val_raw_dir = images_raw_dir / 'val'
            labels_val_raw_dir = labels_raw_dir / 'val'

            all_train_images = list(images_train_raw_dir.rglob('*.jpg'))
            valid_train_data = []
            for img_path in all_train_images:
                label_path = labels_train_raw_dir / f"{img_path.stem}.txt"
                if label_path.exists():
                    valid_train_data.append((img_path, label_path))

            all_val_images = list(images_val_raw_dir.rglob('*.jpg'))
            valid_val_data = []
            for img_path in all_val_images:
                label_path = labels_val_raw_dir / f"{img_path.stem}.txt"
                if label_path.exists():
                    valid_val_data.append((img_path, label_path))

            if not valid_train_data or not valid_val_data:
                print(f"ERROR: [{data_dir}] 원본 이미지 또는 라벨을 찾을 수 없습니다.")
                continue

            random.seed(RANDOM_SEED)
            train_data = random.sample(valid_train_data, TRAIN_SAMPLE_SIZE)
            val_data = random.sample(valid_val_data, VAL_SAMPLE_SIZE)

            print(f"INFO: [{data_dir}] 데이터 샘플링 완료 | train={len(train_data)}, val={len(val_data)}")

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

            print(f"INFO: [{data_dir}] 모든 데이터가 복사되었습니다.")