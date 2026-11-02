(() => {
  const box = document.getElementById('noVNC_clipboard_text');
  if (!box) return;
  // noVNC's native change handler can log text at debug level and send a
  // second clipboard update through VNC. This bridge is the sole paste path.
  box.addEventListener('change', (event) => event.stopImmediatePropagation(), true);
  const button = document.createElement('button');
  button.type = 'button';
  button.textContent = '원격 화면에 붙여넣기';
  const status = document.createElement('div');
  status.setAttribute('role', 'status');
  box.insertAdjacentElement('afterend', status);
  box.insertAdjacentElement('afterend', button);
  button.addEventListener('click', async () => {
    if (!box.value) { status.textContent = '클립보드에 텍스트를 입력하세요.'; return; }
    button.disabled = true;
    status.textContent = '전송 중…';
    try {
      const response = await fetch('/clipboard-paste', {
        method: 'POST', headers: { 'Content-Type': 'text/plain; charset=utf-8' }, body: box.value,
      });
      status.textContent = response.ok ? '전송했습니다. 원격 입력란을 확인하세요.' : '전송 실패: ' + response.status;
    } catch (_) {
      status.textContent = '전송 실패: 연결을 확인하세요.';
    } finally { button.disabled = false; }
  });
})();
