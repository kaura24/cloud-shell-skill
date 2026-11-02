# Cloud Shell Codex Skill

Google Cloud Shell 접속, 편집기 닫기, tmux 업데이트, Codex 또는 Claude Code 설치와 실행, 브라우저 설치까지 안내합니다. Firefox·Chromium WebDriver 검증 도구와 Chromium CDP·Docker Firefox 화면 확인 절차도 포함합니다. Firefox BiDi 및 Docker Chromium은 아직 실환경에서 검증하지 않았습니다.

스킬 본문: [skills/cloud-shell/SKILL.md](skills/cloud-shell/SKILL.md)

공유 Chromium 화면과 한글·영문 클립보드 전달 스킬: [skills/cloud-shell-browser-clipboard/SKILL.md](skills/cloud-shell-browser-clipboard/SKILL.md). 브리지의 실제 Cloud Shell 미리보기와 X11 입력 검증은 별도로 필요합니다.

설치하려면 이 저장소를 클론한 뒤 필요한 `skills/` 하위 스킬 폴더를 Codex의 `~/.codex/skills/`에 복사하고 새 대화를 시작하세요. 기존 폴더가 있으면 먼저 내용을 확인하세요.

Cloud Shell은 임시 실행 환경입니다. 홈 디렉터리의 보존, 세션 종료와 Google Cloud·OpenAI 사용 요금은 스킬에 연결된 공식 문서를 확인하세요.
