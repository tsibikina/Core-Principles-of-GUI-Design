import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root

    // Свойство, которое позволяет задать цвет извне
    property color buttonColor: "grey"

    // Сигнал, который будет испущен при клике
    signal clicked(color selectedColor)

    width: 30
    height: 30
    color: root.buttonColor
    border.width: 2
    border.color: "black"

    MouseArea {
        anchors.fill: parent
        onClicked: {
            // При клике эмитируем сигнал и передаем наш цвет
            root.clicked(root.buttonColor)
        }
    }
}