🧪 AI 기반 과학 서술형 평가 시스템

이 프로젝트는 Streamlit을 활용하여 학생들의 서술형 답안을 수집하고, OpenAI (GPT) API를 통해 실시간으로 채점 및 피드백을 제공하며, Supabase 데이터베이스에 결과를 저장하는 웹 애플리케이션입니다.

📌 주요 기능 (Features)

학생 답안 제출: 학번과 3가지 과학 서술형 문항(기체 운동, 보일 법칙, 열에너지 이동)에 대한 답안을 입력받습니다.

실시간 AI 채점: 제출과 동시에 GPT 모델이 사전에 설정된 채점 기준(Rubric)에 따라 정오답 여부(O/X)를 판별합니다.

맞춤형 피드백: 학생의 답안 내용을 분석하여 200자 이내의 친절하고 구체적인 피드백을 제공합니다.

데이터 클라우드 저장: 학생의 제출 내역과 AI 피드백 결과가 Supabase DB에 자동으로 저장되어 교사가 추후 확인할 수 있습니다.

🖥️ 실행 화면 (Screenshots)

아래 이미지는 예시이며, 실제 실행 화면을 캡처하여 images 폴더에 넣고 경로를 수정하세요.

1. 답안 입력 및 제출 화면

학생이 학번을 입력하고 3개의 서술형 문항에 답을 작성하는 화면입니다.

2. AI 피드백 결과 화면

제출 후 AI가 분석한 채점 결과와 피드백이 실시간으로 표시됩니다.

⚙️ 설치 및 실행 방법 (Installation)

이 프로젝트를 로컬 환경에서 실행하려면 다음 단계가 필요합니다.

1. 환경 설정

파이썬이 설치된 환경에서 필요한 라이브러리를 설치합니다.

pip install streamlit openai supabase


2. Secrets 설정 (.streamlit/secrets.toml)

프로젝트 루트 폴더에 .streamlit 폴더를 만들고 secrets.toml 파일을 생성하여 API 키를 입력합니다.

# .streamlit/secrets.toml

OPENAI_API_KEY = "sk-..."
SUPABASE_URL = "[https://your-project.supabase.co](https://your-project.supabase.co)"
SUPABASE_SERVICE_ROLE_KEY = "your-service-role-key"


3. 애플리케이션 실행

터미널에서 다음 명령어를 입력하여 앱을 실행합니다.

streamlit run app.py


📂 프로젝트 구조 (File Structure)

📦 project-root
 ┣ 📂 .streamlit
 ┃ ┗ 📜 secrets.toml      # API 키 저장소 (깃허브 업로드 금지)
 ┣ 📜 app.py              # 메인 애플리케이션 코드
 ┣ 📜 requirements.txt    # 의존성 패키지 목록
 ┗ 📜 README.md           # 프로젝트 설명 파일


📝 채점 기준 (Grading Guidelines)

AI는 다음 기준에 따라 학생의 답안을 평가합니다.

문항

주제

채점 핵심 키워드

Q1

기체 입자 운동

온도와 비례 관계, 입자 충돌 및 속도 증가

Q2

보일 법칙

일정 온도, 압력과 부피의 반비례 관계

Q3

열에너지 이동

전도(충돌), 대류(순환), 복사(전자기파)

⚠️ 주의사항

이 프로젝트는 교육용 데모 목적으로 제작되었습니다.

secrets.toml 파일이 깃허브에 업로드되지 않도록 .gitignore에 반드시 추가하세요.

Supabase의 테이블(student_submissions)이 미리 생성되어 있어야 정상 작동합니다.
