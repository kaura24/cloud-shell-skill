# Cloud Shell Codex Skill

## 플러그인

이 저장소는 두 스킬을 `cloud-shell-helper` 플러그인으로 묶습니다. `plugin.json`은 Agent Plugins 형식의 플러그인 선언이며 `.agents/plugins/marketplace.json`은 GitHub 워크스페이스 가져오기를 위한 목록입니다. 스킬은 Cloud Shell에 자동으로 접속할 권한을 부여하지 않습니다.

워크스페이스 관리자는 ChatGPT의 **Admin → Plugins → Add → Import marketplace**에서 저장소 URL `https://github.com/kaura24/cloud-shell-skill`을 입력하고 경로는 비워 가져올 수 있습니다. 이후 설치 정책을 설정하고 설치한 계정에서 ChatGPT 웹의 `@` 메뉴로 선택합니다. 이 기능은 워크스페이스 관리자 권한과 플러그인 제공 여부에 따라 달라집니다. GitHub에 파일을 올리는 것만으로 ChatGPT 웹에 등록되지는 않습니다. 개인 계정에서는 [Plugin Creator](https://learn.chatgpt.com/docs/build-plugins)의 제공 여부를 확인해 주세요.

Google Cloud Shell 접속, 편집기 닫기, tmux 업데이트, Codex 또는 Claude Code 설치와 실행, 브라우저 설치까지 안내합니다. Firefox·Chromium WebDriver 검증 도구와 Chromium CDP·Docker Firefox 화면 확인 절차도 포함합니다. Firefox BiDi 및 Docker Chromium은 아직 실환경에서 검증하지 않았습니다.

Codex 터미널 스크롤백과 noVNC 클립보드 문제 해결: [terminal-clipboard-troubleshooting.md](skills/cloud-shell/references/terminal-clipboard-troubleshooting.md).

스킬 본문: [skills/cloud-shell/SKILL.md](skills/cloud-shell/SKILL.md)

공유 Chromium 화면과 한글·영문 클립보드 전달 스킬: [skills/cloud-shell-browser-clipboard/SKILL.md](skills/cloud-shell-browser-clipboard/SKILL.md). 한 Cloud Shell 세션에서 이 브리지의 실제 HTTPS 미리보기와 X11 한글·영문 입력을 검증했습니다. 다른 환경에서는 다시 검증해야 합니다.

설치하려면 이 저장소를 클론한 뒤 필요한 `skills/` 하위 스킬 폴더를 Codex의 `~/.codex/skills/`에 복사하고 새 대화를 시작하세요. 기존 폴더가 있으면 먼저 내용을 확인하세요.

Cloud Shell은 임시 실행 환경입니다. 홈 디렉터리의 보존, 세션 종료와 Google Cloud·OpenAI 사용 요금은 스킬에 연결된 공식 문서를 확인하세요.
