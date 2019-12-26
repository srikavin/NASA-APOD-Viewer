document.getElementById('download-button').addEventListener('click', function () {

    getBase64FromImageUrl('/hdimg?date=' + date).then(dataUrl => {
        const doc = new jsPDF().setProperties({title: raw.title});

        doc.setFontSize(40);
        doc.addImage(dataUrl, 'PNG', 15, 100, 180, 180);
        doc.text(raw.title, 10, 30);
        doc.setFontSize(12);
        doc.text(doc.splitTextToSize(raw.explanation, 180), 10, 60);

        doc.save(raw.title + '.pdf');
    });
});

// Adapted from https://stackoverflow.com/a/16566198/4184530
function getBase64FromImageUrl(url) {
    return new Promise(((resolve, reject) => {
        const img = new Image();
        img.setAttribute('crossOrigin', 'anonymous');

        img.onload = function () {
            const canvas = document.createElement("canvas");
            canvas.width = this.width;
            canvas.height = this.height;

            const ctx = canvas.getContext("2d");
            ctx.drawImage(this, 0, 0);

            const dataURL = canvas.toDataURL("image/png");
            img.remove();
            canvas.remove();

            resolve(dataURL);
        };
        img.onerror = reject;
        img.src = url;
    }));
}