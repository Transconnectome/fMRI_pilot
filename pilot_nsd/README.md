# NSD 방식 이미지 제시 실험 구현

## 개요
이 구현은 **Natural Scenes Dataset (NSD)** 논문(Allen et al., 2022, Nature Neuroscience, doi: 10.1038/s41593-021-00962-x)의 실험 디자인을 따릅니다.

## 주요 특징

### 1. 시행 구조 (NSD 사양)
- **이미지 제시 시간**: 3초
- **공백 간격**: 1초
- **총 시행 시간**: 4초
- **시행 디자인**: 3초 ON / 1초 OFF 구조의 rapid event-related 디자인

### 2. 시각 자극 제시
- **이미지 크기**: 714×714 픽셀 (NSD 셋업에서 8.4° × 8.4° 시각도에 해당)
- **배경색**: 중간 회색 (RGB: 0.5, 0.5, 0.5)
- **고정점**:
  - 반투명 빨간 원 (50% 불투명도)
  - 대비를 위한 검은색 테두리
  - 크기: 0.2° × 0.2° 시각도
  - 이미지 제시 중 중앙에 오버레이

### 3. Run 구조 (NSD 사양)
- **사전 휴식**: 12초 (공백 시행 3개에 해당)
- **자극 시행**: CSV 입력에 따라 가변
- **사후 휴식**: 16초 (공백 시행 4개에 해당)
- **총 run 시간**: 자극 시행 63개 기준 약 300초 (NSD 표준)

### 4. 과제 디자인
- **연속 재인 기억 과제**
- 버튼 1: "새로운" 이미지 (이전에 본 적 없음)
- 버튼 2: "본 적 있는" 이미지 (실험 초반에 제시되었던 이미지)
- 이미지 제시와 공백 간격 모두에서 반응 수집
- 이미지 onset 기준으로 반응 시간 기록

### 5. 스캐너 연동
- **스캐너 트리거 지원**: 트리거 키 대기 (기본값: '5')
- **트리거 로깅**: PsychoPy 클럭 시간과 시스템 날짜/시간 모두 기록
- **BIDS 호환 출력**: 표준화된 구조로 이벤트를 TSV 형식으로 저장

## 파일 구조

### 생성된 파일
1. **nsd_image_experiment.py** - 메인 실험 스크립트
2. **test_image_list.csv** - 이미지 목록을 위한 템플릿 CSV
3. **README.md** - 이 문서

### 입력 CSV 형식
```csv
session,run,image_path,order,is_repeat
1,1,"/path/to/images/img_001.png",1,0
1,1,"/path/to/images/img_002.png",2,0
1,1,"/path/to/images/img_001.png",3,1
```

**컬럼 설명:**
- `session`: 세션 번호 (정수)
- `run`: 세션 내 run 번호 (정수)
- `image_path`: 이미지 파일의 전체 경로
- `order`: run 내 시행 순서 (정수)
- `is_repeat`: 0=새 이미지, 1=반복 이미지

### 출력 파일 (BIDS 형식)
```
nsd_outputs/
└── sub-{피험자ID}/
    └── ses-{세션번호}/
        ├── run-{Run번호}.events.tsv     # 시행별 데이터
        └── run-{Run번호}.scan_times.txt  # 스캐너 트리거 타임스탬프
```

## 사용법

### 기본 사용
```bash
python nsd_image_experiment.py \
    --sub_id 01 \
    --session 1 \
    --image_csv_path /path/to/image_list.csv
```

### 맞춤 설정을 사용한 고급 사용
```bash
python nsd_image_experiment.py \
    --sub_id 01 \
    --session 1 \
    --image_csv_path /path/to/image_list.csv \
    --output_dir custom_output \
    --image_duration 3.0 \
    --blank_duration 1.0 \
    --image_size_pixels 714 \
    --use_scanner_trigger \
    --trigger_key 5 \
    --collect_responses \
    --new_key 1 \
    --old_key 2
```

### 명령줄 인자

#### 필수
- `--image_csv_path`: 이미지 경로와 시행 구조를 담은 CSV 파일 경로

#### 피험자/세션
- `--sub_id`: 피험자 ID (기본값: "01")
- `--session`: 세션 번호 (기본값: 1)
- `--output_dir`: 출력 디렉토리 경로 (기본값: "nsd_outputs")

#### 타이밍 (NSD 기본값)
- `--image_duration`: 이미지 제시 시간(초) (기본값: 3.0)
- `--blank_duration`: 공백 간격 시간(초) (기본값: 1.0)
- `--prerest`: 초기 공백 시간(초) (기본값: 12.0)
- `--postrest`: 마지막 공백 시간(초) (기본값: 16.0)

#### 디스플레이
- `--image_size_pixels`: 이미지 크기(픽셀) (기본값: 714, 8.4° 시각도용)
- `--fixation_size_deg`: 고정점 크기(도) (기본값: 0.2)
- `--fixation_opacity`: 고정점 불투명도 (기본값: 0.5)

#### 스캐너
- `--use_scanner_trigger`: 시작 시 스캐너 트리거 대기 (플래그, 기본값: True)
- `--trigger_key`: 스캐너 트리거 키 (기본값: "5")

#### 반응 수집
- `--collect_responses`: 반응 수집 활성화 (플래그, 기본값: True)
- `--new_key`: "새 이미지" 반응 버튼 (기본값: "1")
- `--old_key`: "본 이미지" 반응 버튼 (기본값: "2")

#### 실험 제어
- `--shuffle_images`: run 내 이미지 순서 섞기 (플래그, 기본값: False)

## NSD 논문 참고사항

### 원본 실험 매개변수
Allen et al. (2022), Methods 섹션에서:

**시각 자극:**
> "Images were presented using Psychophysics Toolbox (version 3.0.14) in MATLAB on a BOLDscreen LCD monitor (Cambridge Research Systems, 1920 × 1080, 120 Hz)... prepared NSD images were resized using linear interpolation from their native resolution of 425 pixels × 425 pixels to 714 pixels × 714 pixels to occupy 8.4° × 8.4° on the display"

**시행 타이밍:**
> "images were presented using a 3-s ON/1-s OFF trial structure... rapid event-related design was chosen to maximize statistical power"

**고정점:**
> "a small semi-transparent red fixation dot with a black border (0.2° × 0.2°, 50% opacity) was present at the center of the stimuli"

**과제:**
> "participants were instructed to fixate the central dot and to press button 1 using the index finger of their right hand if the presented image was new... or button 2 using the middle finger of their right hand if the presented image was old"

**Run 구조:**
> "Each run lasted 300 s... The first three trials (12 s) and the last four trials (16 s) were blank trials. The remaining 68 trials were divided into 63 stimulus trials and five blank trials"

**세션 구조:**
> "12 NSD runs were collected in one NSD session... yielding a total of (63+62) × 6=750 stimulus trials"

## 구현 참고사항

### 원본 NSD와의 차이점
1. **이미지 소스**: 원본은 COCO 데이터셋 이미지 사용; 이 구현은 모든 이미지 파일 허용
2. **반복 스케줄**: 원본은 복잡한 세션 간 반복 체계 사용; 이것은 간단한 CSV 기반 제어
3. **공백 시행 분포**: 원본은 5개 공백 시행을 무작위 삽입; 이것은 사전/사후 공백만 사용
4. **세션 크기**: 원본은 세션당 12 runs; 이것은 유연한 run 수 허용

### 기술적 고려사항
1. **시각도 보정**: 714픽셀 크기는 특정 관찰 거리와 모니터 DPI를 가정
2. **타이밍 정밀도**: PsychoPy는 밀리초 수준의 타이밍 정확도 제공
3. **반응 윈도우**: 이미지 onset부터 공백 간격까지 확장 (총 4초)
4. **스캐너 동기화**: 첫 트리거가 t=0에서 실험 클럭 시작

## 기존 스크립트와의 비교

### horikawa_pilot_scanner.py (비디오 제시)
- **자극**: 가변 길이 비디오
- **타이밍**: TR 정렬을 위한 유연한 REST
- **과제**: 수동 관찰
- **시행 구조**: 비디오 길이에 따라 가변

### audio_fmri_experiment.py (오디오 제시)
- **자극**: 가변 길이 오디오 파일
- **타이밍**: TR 정렬을 위한 유연한 REST
- **과제**: 수동 청취
- **시행 구조**: 오디오 길이에 따라 가변

### nsd_image_experiment.py (이 구현)
- **자극**: 고정 크기 정적 이미지
- **타이밍**: 고정 3초 ON / 1초 OFF 구조 (rapid event-related)
- **과제**: 능동적 연속 재인 기억
- **시행 구조**: 고정 4초 시행

## 품질 관리

### Run 전 체크리스트
- [ ] CSV 파일이 존재하고 경로가 정확함
- [ ] 모든 이미지 파일이 지정된 경로에 존재함
- [ ] 이미지가 적절한 해상도임 (권장: ≥714×714 픽셀)
- [ ] 스캐너 트리거 키가 올바르게 설정됨
- [ ] 피험자가 반응 버튼에 접근 가능함

### Run 중 모니터링
- PsychoPy 콘솔에서 오류 메시지 확인
- 피험자가 적절히 반응하는지 확인
- 실험 타이밍 모니터링 (63 시행 기준 ~300초)

### Run 후 검증
- events.tsv에서 적절한 타이밍 확인 (4초 시행)
- 반응 데이터가 기록되고 있는지 확인
- 이미지 제시 순서가 CSV와 일치하는지 확인
- 로그 파일에서 경고나 오류 검토

## 문제 해결

### 일반적인 문제

**이미지가 표시되지 않음:**
- CSV의 이미지 파일 경로 확인
- 이미지 파일 형식 확인 (PNG, JPG 지원)
- 이미지 파일 권한 확인

**타이밍 드리프트:**
- CPU를 소비하는 다른 프로세스가 없는지 확인
- PsychoPy에서 프레임 레이트 안정성 확인
- 로그 파일에서 드롭된 프레임 확인

**스캐너 트리거 없음:**
- 트리거 키가 올바른지 확인
- 스캔 전에 트리거 키를 수동으로 테스트
- 스캐너 출력 구성 확인

**반응이 기록되지 않음:**
- 반응 키가 올바른지 확인
- 키보드 연결 확인
- `--collect_responses` 플래그가 설정되었는지 확인

## 향후 개선사항

전체 NSD 디자인과 일치시키기 위한 잠재적 추가사항:
1. **공백 시행 분포**: 자극 시행 내에 공백 시행을 무작위로 삽입
2. **다중 이미지 제시**: 각 이미지를 세션에 걸쳐 3회 제시 (NSD 디자인)
3. **세션 수준 반복 추적**: 복잡한 세션 간 반복 스케줄
4. **COCO 데이터셋 통합**: COCO 데이터셋에서 자동 이미지 선택
5. **시선 추적 통합**: 고정 준수를 위한 응시 모니터링
6. **다중 세션 관리**: 자동 세션 진행 및 이미지 할당

## 참고문헌

Allen, E.J., St-Yves, G., Wu, Y. et al. A massive 7T fMRI dataset to bridge cognitive neuroscience and artificial intelligence. *Nat Neurosci* **25**, 116–126 (2022). https://doi.org/10.1038/s41593-021-00962-x

## 연락처

이 구현에 대한 질문은 원본 NSD 논문의 methods 섹션 또는 Natural Scenes Dataset 문서(http://naturalscenesdataset.org/)를 참조하세요.
