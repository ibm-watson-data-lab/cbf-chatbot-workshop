var editor = undefined;
require(['vs/editor/editor.main'], function() {
	editor = monaco.editor.create(document.getElementById('editor'), {
		readOnly: true,
		theme: 'vs-dark',
		language: 'json',
		automaticLayout: true
	});
});