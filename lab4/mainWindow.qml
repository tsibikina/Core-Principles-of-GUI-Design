import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15

ApplicationWindow {
    id: root
    visible: true
    width: 900
    height: 700
    title: "Графический редактор с двойной системой сохранения"

    // --- Таймер для автосохранения в историю (saves.json) ---
    Timer {
        id: autoSaveHistoryTimer
        interval: 60000 // 1 минута по умолчанию
        running: false
        repeat: true
        onTriggered: {
            console.log("Автосохранение в историю...")
            drawingBackend.saveCanvas(canvas.toDataURL())
        }
    }

    // --- Таймер для умного автосохранения в PNG (каждые 30 сек) ---
    Timer {
        id: autoSavePngTimer
        interval: 30000 // 30 секунд
        running: true // Запускаем сразу и всегда
        repeat: true
        onTriggered: {
            console.log("Автосохранение в PNG...")
            drawingBackend.autoSaveToPng(canvas.toDataURL())
        }
    }

    function setAutoSaveHistoryTimer(intervalMs) {
        autoSaveHistoryTimer.interval = intervalMs
        if (intervalMs > 0) {
            autoSaveHistoryTimer.restart()
        } else {
            autoSaveHistoryTimer.stop()
        }
    }

    ColumnLayout {
        anchors.fill: parent
        spacing: 10

        // --- Панель инструментов ---
        RowLayout {
            Layout.fillWidth: true
            Layout.margins: 10

            Label { text: "Цвет:" }
            Row {
                spacing: 5
                Square { buttonColor: "#FF0000"; onClicked: canvas.currentColor = buttonColor }
                Square { buttonColor: "#00FF00"; onClicked: canvas.currentColor = buttonColor }
                Square { buttonColor: "#0000FF"; onClicked: canvas.currentColor = buttonColor }
                Square { buttonColor: "#000000"; onClicked: canvas.currentColor = buttonColor }
            }

            Item { Layout.fillWidth: true }

            Label { text: "Толщина:" }
            Row {
                spacing: 5
                Circle { id: w1Btn; value: 1; selected: true; onClicked: updateWidthSelection(value) }
                Circle { id: w2Btn; value: 2; onClicked: updateWidthSelection(value) }
                Circle { id: w3Btn; value: 3; onClicked: updateWidthSelection(value) }
                Circle { id: w4Btn; value: 4; onClicked: updateWidthSelection(value) }
                Circle { id: w5Btn; value: 5; onClicked: updateWidthSelection(value) }
            }
        }

        // --- Основная область с холстом и историей ---
        RowLayout {
            Layout.fillWidth: true
            Layout.fillHeight: true
            Layout.margins: 10

            Rectangle {
                Layout.fillWidth: true
                Layout.fillHeight: true
                color: "white"
                border.color: "grey"

                Canvas {
                    id: canvas
                    anchors.fill: parent
                    anchors.margins: 1

                    property string currentColor: "#000000"
                    property int lineWidth: 2
                    property var strokes: []
                    property var currentStrokePoints: []
                    property string imageToLoad: ""
                    property bool isDrawing: false

                    onImageLoaded: requestPaint()

                    onPaint: {
                        var ctx = getContext("2d")
                        ctx.clearRect(0, 0, width, height)
                        if (isImageLoaded(imageToLoad)) {
                            ctx.drawImage(imageToLoad, 0, 0)
                        }
                        for (var i = 0; i < strokes.length; i++) {
                            var stroke = strokes[i];
                            ctx.strokeStyle = stroke.color; ctx.lineWidth = stroke.width; ctx.lineCap = "round";
                            ctx.beginPath(); ctx.moveTo(stroke.points[0].x, stroke.points[0].y);
                            for (var j = 1; j < stroke.points.length; j++) { ctx.lineTo(stroke.points[j].x, stroke.points[j].y); }
                            ctx.stroke();
                        }
                        if (isDrawing && currentStrokePoints.length > 0) {
                            ctx.strokeStyle = currentColor; ctx.lineWidth = lineWidth; ctx.lineCap = "round";
                            ctx.beginPath(); ctx.moveTo(currentStrokePoints[0].x, currentStrokePoints[0].y);
                            for (var k = 1; k < currentStrokePoints.length; k++) { ctx.lineTo(currentStrokePoints[k].x, currentStrokePoints[k].y); }
                            ctx.stroke();
                        }
                    }

                    MouseArea {
                        id: mouseArea
                        anchors.fill: parent
                        onPressed: { canvas.isDrawing = true; canvas.currentStrokePoints = [Qt.point(mouseX, mouseY)]; canvas.requestPaint(); }
                        onPositionChanged: { if (canvas.isDrawing) { canvas.currentStrokePoints.push(Qt.point(mouseX, mouseY)); canvas.requestPaint(); } }
                        onReleased: {
                            if (canvas.isDrawing && canvas.currentStrokePoints.length > 0) {
                                canvas.strokes.push({"color": canvas.currentColor, "width": canvas.lineWidth, "points": canvas.currentStrokePoints});
                            }
                            canvas.isDrawing = false; canvas.currentStrokePoints = []; canvas.requestPaint();
                        }
                    }
                }
            }

            // --- Панель истории сохранений ---
            Rectangle {
                Layout.preferredWidth: 200
                Layout.fillHeight: true
                color: "#f0f0f0"
                border.color: "grey"
                ColumnLayout {
                    anchors.fill: parent; anchors.margins: 5
                    Label { text: "История (saves.json)"; font.bold: true; Layout.alignment: Qt.AlignHCenter }
                    ListView {
                        id: historyView; Layout.fillWidth: true; Layout.fillHeight: true
                        model: drawingBackend.historyModel; delegate: historyDelegate; clip: true
                    }
                }
            }
        }

        // --- Нижняя панель управления ---
        RowLayout {
            Layout.fillWidth: true; Layout.margins: 10
            Label { text: "Автосохранение в историю:" }
            ComboBox {
                id: autoSaveCombo; model: ["Выкл", "30 сек", "1 мин", "5 мин", "10 мин"]; currentIndex: 2
                onCurrentIndexChanged: {
                    var intervals = [0, 30, 60, 300, 600]
                    var intervalSec = intervals[currentIndex]
                    drawingBackend.setAutoSaveInterval(intervalSec)
                    root.setAutoSaveHistoryTimer(intervalSec * 1000)
                }
                Component.onCompleted: {
                    var intervals = [0, 30, 60, 300, 600]
                    drawingBackend.setAutoSaveInterval(intervals[currentIndex])
                    root.setAutoSaveHistoryTimer(intervals[currentIndex] * 1000)
                }
            }
            Item { Layout.fillWidth: true }
            Button { text: "Сохранить в историю"; onClicked: drawingBackend.saveCanvas(canvas.toDataURL()) }
            Button { text: "Очистить"; onClicked: { canvas.strokes = []; canvas.imageToLoad = ""; canvas.requestPaint(); } }
        }

        // --- Строка статуса ---
        RowLayout {
            Layout.fillWidth: true
            Layout.margins: 10
            Label {
                id: statusLabel
                text: "PNG-бэкап: autosave_backup.png (каждые 30 сек)"
                font.pixelSize: 12
                color: "gray"
            }
        }
    }

    // --- Делегат для элементов списка истории ---
    Component {
        id: historyDelegate
        Item {
            width: historyView.width; height: 120
            Rectangle {
                anchors.fill: parent; anchors.margins: 2; color: "white"; border.color: "lightgrey"
                Column {
                    anchors.fill: parent; anchors.margins: 5
                    Image { width: parent.width; height: 90; source: "data:image/png;base64," + imageData; fillMode: Image.PreserveAspectFit }
                    Text { text: timestamp; font.pixelSize: 12; anchors.horizontalCenter: parent.horizontalCenter }
                }
                MouseArea { anchors.fill: parent; onClicked: drawingBackend.loadSave(index) }
            }
        }
    }

    // --- Функция для обновления выделения кнопок толщины ---
    function updateWidthSelection(selectedValue) {
        w1Btn.selected = (selectedValue === 1);
        w2Btn.selected = (selectedValue === 2);
        w3Btn.selected = (selectedValue === 3);
        w4Btn.selected = (selectedValue === 4);
        w5Btn.selected = (selectedValue === 5);
        canvas.lineWidth = selectedValue;
    }

    // --- Обработчик сигнала о статусе сохранения ---
    Connections {
        target: drawingBackend
        function onSaveStatusChanged(message) {
            statusLabel.text = message
            resetStatusTimer.restart()
        }
    }

    // Таймер для сброса текста статуса
    Timer {
        id: resetStatusTimer
        interval: 5000
        onTriggered: {
            statusLabel.text = "PNG-бэкап: autosave_backup.png (каждые 30 сек)"
        }
    }
}