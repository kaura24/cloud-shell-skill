# Cloud Shell 터미널과 클립보드 문제 해결

사용자가 방법만 원하면 명령을 안내하고 직접 조작하지 않는다. 기존 설정, 프로필과 실행 중인 프로세스를 확인해 보존한다. 인증 정보나 클립보드 본문을 로그·공개 저장소에 기록하지 않는다.

## Codex 터미널 스크롤

긴 출력이 잘리거나 스크롤되지 않을 때 증상을 먼저 재현하고 버전과 tmux 상태를 확인한다.

```bash
codex --version
tmux -V
tmux list-panes -a -F '#{session_name}:#{window_index}.#{pane_index} cmd=#{pane_current_command} mode=#{pane_in_mode} alternate=#{alternate_on} history=#{history_size}'
tmux show-options -g | grep -E 'mouse|history-limit|default-terminal'
```

Cloud Shell은 이미 tmux 안에서 실행될 수 있다. `sessions should be nested with care`는 중첩 시도 경고이며 미설치의 증거가 아니다. 서버를 강제로 종료하거나 새 세션을 억지로 만들지 않는다. tmux 복사 모드는 `Ctrl+B`를 누르고 손을 뗀 뒤 `[`, 방향키 또는 Page Up으로 이동하고 `q`로 빠져나온다. 이를 안내했다고 실제 문제가 해결됐다고 단정하지 않는다.

Codex 버전에서 지원하는지 [공식 설정 문서](https://learn.chatgpt.com/docs/config-file/config-reference)와 해당 CLI 도움말을 확인한다. 지원되는 경우 아래 설정은 스크롤백과 복사에 도움을 줄 수 있다.

```toml
[tui]
alternate_screen = "never"
raw_output_mode = true
```

대상 파일은 `~/.codex/config.toml`이다. 수정 전에 기존 파일과 `[tui]`를 읽고 같은 테이블을 중복 생성하지 않으며 다른 설정이나 사용자가 선택한 값을 보존한다. 수정 후 TOML 구문을 검증한다. 실행 중인 Codex를 임의로 종료하지 않는다. 새 설정이 다음 실행에서 반영될 수 있음을 알리고 `codex resume` 또는 사용자가 보유한 세션 ID로 다시 열도록 안내한다. 지원되는 경우 `/raw` 또는 기본 `Alt+R`로 원시 스크롤백 모드를 전환할 수 있다. 설정 파싱 성공, 대체 화면 전환 여부, **사용자 화면에서의 스크롤 성공**은 별도로 보고한다.

## noVNC·클립보드 진단

사용자가 보는 noVNC와 Codex의 CDP가 같은 Chromium 인스턴스인지 확인하고, 기존 프로필·탭·로그인을 보존한다. Cloud Shell 세션마다 `cloudshell get-web-preview-url -p 8080`을 시도해 현재 주소를 확인한다. 명령 실패 시 `cloudshell help`와 웹 미리보기 UI로 확인하고 이전 주소를 고정하지 않는다. 브라우저 디버깅과 VNC는 localhost에 두고 인증된 미리보기를 이용한다.

버튼이 보이지 않으면 **실제로 제공 중인 HTML과 JavaScript**에 버튼과 이벤트 연결이 들어 있는지, 올바른 서버에 접속했는지, CSS·화면 크기 때문에 가려졌는지, 브라우저 또는 미리보기 캐시가 낡았는지 순서대로 확인한다. 필요한 경우 스크립트 URL에 버전 쿼리를 붙여 캐시를 구분한다. 기존 파일을 교체하기 전에 확인하고 보존한다.

버튼은 사용자가 원격 Chromium의 대상 입력란을 먼저 선택하고 noVNC 클립보드 보드에 입력한 한글·영문을 UTF-8로 원격 X11 클립보드에 전달한 뒤 해당 입력란에 붙여넣어야 한다. x11vnc의 기본 동기화가 중복 전송하거나 한글을 덮어쓰는지 검사하고, 충돌 시 기존 세션에 미치는 영향을 사용자에게 설명한 후 `-nosel`을 검토한다. 별도 클립보드 브리지 구현은 exact Origin 비교, 요청 크기 제한, UTF-8, 로그 비기록, 로컬 바인딩을 갖춰야 한다. Host 헤더만 믿거나 와일드카드를 허용하지 않는다. `cloud-shell-browser-clipboard` 스킬의 브리지가 설치되어 있다면 그 절차와 실제 동작을 먼저 확인한다.

localhost에서 테스트 성공만으로 완료라고 하지 않는다. 현재 세션의 실제 인증된 HTTPS 미리보기에서 테스트 입력란에 비밀이 아닌 한글·영문·숫자를 넣고 정확히 일치하는지 확인한다. 테스트용 탭과 자원만 정리한다. 버튼 표시, 클립보드 전송, 실제 입력란 일치, 사용자 화면에서의 확인을 분리해 보고한다. 실환경 테스트가 불가능하면 그 한계를 명시한다.

## 재접속

기본 Cloud Shell의 홈 디렉터리는 보존되지만 VM, 프로세스, 홈 밖의 패키지와 Docker 데이터는 유지된다고 가정하지 않는다. 재접속 후 저장된 홈의 설정·프로필·스크립트를 확인하고 필요한 패키지만 복구한다. 홈은 영구 백업을 대신하지 않는다.
