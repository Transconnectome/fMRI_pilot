fMRI Experimental Protocol and Paradigm : Seokjin Moon, Taeyang Lee
(Based on Horikawa et al., 2020 – The Neural Representation of Visually Evoked Emotion Is High-Dimensional, Categorical, and Distributed Across Transmodal Brain Regions)

Department of Brain & Cognitive Sciences
Connectome Lab (Prof. Jiook Cha)
Written by SeokJin Moon, Taeyang Lee

1. 연구 개요 (Introduction)
본 연구는 Horikawa et al. (2020)에서 제시된 Visually Evoked Emotion fMRI paradigm을 완전 재현(replicate)하는 것을 기본으로 하되, 추가적으로 서사적 감정 변화를 포함한 단편 애니메이션(short film)과 음악 자극(music)을 결합하여 확장한 형태로 설계되었다.
즉, 본 연구는 세 가지 자극 유형을 포함한다:
(1) 시각적 무음 영상 (Horikawa et al., 2020),
(2) 감정 서사를 지닌 단편 애니메이션 One Small Step (Vaccaro et al., 2024),
(3) 음악 기반 감정 자극 (McClay et al., 2023).

2. 연구 방법 (Methods)
2.1 Participants and Session Structure
본 실험은 1–2명의 피험자를 대상으로 수행되며, 모든 참가자는 정상 또는 교정 시력 및 청력을 가진 성인으로 모집된다. 각 피험자는 총 9회의 fMRI session(session)에 참여하며, 각 session의 길이는 약 60–90분이다. session 간 최소 24시간의 간격을 유지하여 피로 누적과 정서적 habituation을 방지한다. 
session 전후로 사전/사후 설문(pre/post-experiment survey)을 시행하여 참가자의 인구통계 정보, 정서 상태(우울, 불안 척도 포함), 실험 중 피로도 및 몰입도 등을 측정한다. 모든 설문은 Google form 으로 진행되며 응답은 익명화된다.


2.2 Stimulus Presentation
(a) Horikawa Visual Stimuli
Horikawa et al. (2020)의 연구에 사용된 2,181개의 짧은 무음 비디오 클립 전체를 자극으로 사용한다. 각 영상은 평균 5–10초 길이의 무음 시각 자극으로, 인간, 동물, 자연, 사회적 상호작용 등 다양한 감정적 상황을 포함한다. 각 영상은 화면 중앙에 12° 시야각(visual angle)으로 제시되며, 배경은 중간 회색(mid-gray / 128,128,128)으로 설정된다. 원 연구의 재현성을 극대화하기 위해, 자극 제시 순서 및 session과 run(run) 구성은 원본 연구를 그대로 따른다.
   

(b) Narrative Short Film (One Small Step)
Vaccaro et al. (2024)에서 사용된 단편 애니메이션 One Small Step (2018) 을 사용한다. 이 영상은 뚜렷한 서사 구조를 통해 긍정, 부정, 그리고 복합적인 감정 상태의 전이를 자연스럽게 유도한다. 본 연구에서는 이 영상을 별도의 fMRI run으로 삽입하여, 서사적 맥락을 지닌 장기적 감정 전이가 뇌의 활동 패턴에서 어떻게 반영되는지를 탐색한다. 영상은 무음 상태로 제시되며, Horikawa 자극과 동일한 시각적 세팅을 유지하도록 한다.

(c) Musical Stimuli
McClay et al. (2023)의 연구를 기반으로 설계된 음악 자극 세트(10개)를 사용한다. 자극은 전문 작곡가들이 작곡한 오리지널 오케스트라 음원으로, 기쁨(joyous), 불안(anxious), 슬픔(sad), 평온(calm)의 네 가지 감정 테마를 유발하도록 설계되었다. 각 음원은 약 120초 길이로, 3개의 뚜렷한 감정 구간(30-40초)과 그 사이를 잇는 전환 구간(6-9초)을 포함한다. 음악은 스캐너 내 헤드폰을 통해 제시되며, 피험자는 화면 중앙에 제시되는 회색 배경의 fixation cross를 응시하도록 한다.

2.3 Experimental Procedure & Run Structure (Block design)
실험 시작 전, 피험자에게 본 연구의 목표는 자극이 지닌 객관적인 감정 속성(예: '이 영상은 슬픈 영상이다')을 평가하는 것이 아니라, 각 자극을 경험하는 동안 주관적으로 느껴지는 자신의 감정(예: '이 영상을 보니 슬프다')에 집중하는 것임을 명확히 안내하도록 한다.
본 실험은 총 9회의 Main Session으로 구성된다. 이 중 8개 session은 Horikawa et al. (2020)의 시각 자극 패러다임 재현에 할당되며, 마지막 1개 session은 서사 영상(One Small Step) 및 음악 자극 과제를 위해 별도로 진행된다. 모든 session은 본 과제 시작 전, 피험자의 과제 절차 및 fMRI 환경 적응을 돕기 위한 Practice Block으로 시작한다. 모든 자극 제시는 PsychoPy 소프트웨어를 사용하여 제어된다.

2.3.1 Main Sessions 1–8: Horikawa Visual Stimuli Paradigm 
총 61개의 Horikawa 영상 자극 run을 8개의 session에 걸쳐 분배하여 진행한다 (Session per 7-8 runs). 각 session의 절차는 다음과 같다.
•	Practice Runs: 각 session의 본 과제 시작 전, 피험자는 3-5개의 짧은(약 5-10초) 중립적인 유튜브 영상 클립을 시청하는 연습 시행을 수행한다. 이를 통해 피험자는 스캐너 내 영상 시청 환경에 적응하는 시간을 갖는다. 자극 제시에 관한 모든 사항은 Horikawa 와 동일하게 적용한다.
•	Horikawa Runs:
o	Run Structure: 각 run은 다음의 순차적 구조를 따른다:
32초 Baseline Rest → 36회 Stimulus Blocks → 6초 End Rest
o	Stimulus Block : 하나의 block은 영상 제시 구간과 그 뒤에 오는 2초의 Inter-Block Rest로 구성된다.
	영상 길이 < 8초: 총 제시 시간이 8초를 초과할 때까지 영상이 반복 재생된다.
	영상 길이 ≥ 8초: 영상이 1회 재생된다. 이때, block의 총 길이가 TR(2초)의 배수가 되도록 영상 뒤에 짧은 rest가 추가될 수 있다.
•	피험자 과제: 피험자는 영상이 제시되는 동안에는 자유롭게 시청하며(free-viewing), 모든 rest 기간(baseline, inter-block, end rest)에는 화면 중앙의 고정 십자(fixation cross)를 응시한다.
 
 
2.3.2 Main Session 9: Narrative and Musical Stimuli Paradigm 
마지막 세션은 서사 영상 과제와 음악 자극 과제를 순차적으로 진행하며, 각 과제 시작 전 별도의 Practice Block을 포함한다.
(a) Narrative Video Stimulus Run
•	Practice Block: 본격적인 과제에 앞서, 피험자는 3-5개의 중립적인 유튜브 영상 클립을 시청하는 연습 block을 수행한다.
•	Run Structure: Vaccaro et al. (2024)의 연구 절차에 따라, 약 454초(7분 34초) 길이의 애니메이션 One Small Step 전체를 하나의 독립된 run으로 제시한다. 영상은 중간 rest 없이 한 번에 연속적으로 상영된다.
32초 Baseline Rest → 454초 Stimuli Block → 6초 End Rest
•	피험자 과제: 피험자는 영상이 제시되는 동안에는 자유롭게 시청하며(free-viewing), 모든 rest 기간(baseline rest, end rest)에는 화면 중앙의 고정 십자(fixation cross)를 응시한다.

(b) Musical Stimuli Runs
•	Practice Block: 음악 자극 과제 시작 전, 피험자는 McClay et al. (2023) 연구에서 사용된 별도의 연습용 음원('dreamy' 테마)을 이용한 1회의 Practice Block을 수행하여 과제 방식에 익숙해진다.
•	Run Structure: 총 10개의 음악 자극이 각각 하나의 독립된 run(총 10 runs)으로 제시된다.
o	각 run은 약 120초 길이의 음악 한 곡으로 구성된다.
•	피험자 과제: 피험자는 fMRI 호환 헤드폰을 통해 음악을 감상하며, 화면 중앙에 제시되는 고정 십자(fixation cross)를 응시하도록 지시 받는다. 이 run 동안에는 별도의 이미지 제시가 없다.
 
2.4 Post-scan Behavioral Rating
모든 fMRI 세션 완료 후, 피험자는 별도의 행동 실험실에서 자극에 대한 연속적인 감정 평가(continuous emotion rating)를 수행한다. 
•	Rating Procedure: 세션이 끝나면, 피험자는 fMRI 실험에서 제시되었던 모든 시각 자극(Horikawa 영상, One Small Step)과 청각 자극(음악)을 다시 경험한다. 자극이 제시되는 동안, 피험자는 조이스틱(joystick) 또는 다이얼(dial) 장치를 사용하여 실시간으로 느껴지는 감정의 두 가지 핵심 차원(core affective dimensions)을 평가한다.
o	Valence: 감정의 긍정-부정 차원 (매우 불쾌함 ~ 매우 유쾌함).
o	Arousal: 감정의 각성-진정 차원 (매우 차분함 ~ 매우 흥분됨).
•	Data Collection: 평가 데이터는 100ms 간격(10Hz)으로 샘플링되어, 자극 제시 시점과 동기화(synchronize)된 연속적인 시계열(time-series) 데이터로 저장된다. 이 데이터는 추후 fMRI 데이터의 TR에 맞춰 다운샘플링(down-sampling)되어 분석에 사용된다. 이 과정을 통해, 원 연구에서 사용된 집단 평균(group-averaged) 평점과 더불어, 피험자 개인의 역동적인(dynamic) 감정 변화 궤적을 확보한다.

2.5 fMRI Data Acquisition
2.6 fMRI Data Preprocessing
획득된 모든 fMRI 데이터는 Horikawa et al. (2020)의 연구 절차를 엄격하게 준수하여 전처리한다. 전처리 과정은 fMRIPrep 파이프라인을 기본으로 사용하며, 이후 추가적인 분석을 위한 맞춤형 단계를 포함한다.
•	1단계: fMRIPrep을 이용한 기본 전처리 fMRIPrep 파이프라인을 사용하여 다음과 같은 표준 전처리 과정을 수행한다.
o	BOLD 기준 영상 생성 (BOLD Reference Image Generation)
o	민감도 왜곡 보정 (Susceptibility Distortion Correction)
o	두부 움직임 보정 (Head Motion Correction)
o	슬라이스 시간 보정 (Slice Timing Correction)
o	공동 등록 (Co-registration)
o	공간 재구성 (Resampling)
•	2단계: 분석을 위한 데이터 샘플 생성 fMRIPrep으로 전처리된 BOLD 신호에 대해 Horikawa et al. (2020)의 후속 처리 절차를 적용하여 최종 분석용 데이터 샘플을 생성한다.
o	노이즈 회귀 제거 (Nuisance Regression): 각 run의 복셀 시계열 데이터에서 베이스라인(constant baseline), 선형 추세(linear trend), 그리고 움직임 보정 과정에서 산출된 6개의 움직임 파라미터(3개 회전, 3개 이동)를 회귀 변수로 설정하여 제거한다.
o	혈류역학 지연 보정 (Hemodynamic Delay Correction): 혈류역학적 반응 지연을 고려하여 모든 시계열 데이터를 4초(2 TRs)만큼 시간적으로 이동시킨다.
o	이상치 제거 (Despiking): 각 run 내에서 ±3 표준편차를 벗어나는 극단적인 값들을 줄인다.
o	블록 평균화 (Block Averaging): 각 자극 블록(영상 제시 기간 + 이후 2초 휴지기) 내의 신호를 평균하여 개별 자극에 대한 단일 반응 값을 산출한다.
o	표준화 (Standardization): 최종적으로, 모든 자극에 대한 데이터를 각 복셀 단위로 z-점수화(z-score)하여 복셀 간의 기본 활성화 수준 차이를 정규화한다.

<img width="451" height="678" alt="image" src="https://github.com/user-attachments/assets/57596ba0-1975-4e00-a639-c51d256000f1" />
