import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: root

    // Свойства для настройки извне
    property int value: 1
    property bool selected: false

    // Сигнал, который будет испущен при клике
    signal clicked(int selectedValue)

    width: 35
    height: 35
    radius: width / 2 // Делаем прямоугольник кругом
    color: "white"
    border.width: 3
    // Цвет рамки зависит от того, выбрана ли кнопка
    border.color: root.selected ? "blue" : "darkgrey"

    Text {
        anchors.centerIn: parent
        text: root.value
        font.bold: true
        color: root.selected ? "blue" : "black"
    }

    MouseArea {
        anchors.fill: parent
        onClicked: {
            // При клике эмитируем сигнал и передаем значение толщины
            root.clicked(root.value)
        }
    }
}