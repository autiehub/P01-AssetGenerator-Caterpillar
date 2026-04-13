import random

import maya.cmds as cmds
from PySide6 import QtWidgets, QtCore

WINDOW_NAME = "CaterpillarGeneratorUI"


class CaterpillarGenerator(QtWidgets.QWidget):

    def __init__(self):
        super(CaterpillarGenerator, self).__init__()

        self.setWindowTitle("Procedural Caterpillar Generator")
        self.setMinimumWidth(300)

        self.create_ui()
        self.create_connections()


    def create_ui(self):

        layout = QtWidgets.QVBoxLayout(self)

        self.segment_slider = self.slider("Segments", 3, 20, 8)
        self.size_slider = self.slider("Segment Size", 1, 10, 3)
        self.spacing_slider = self.slider("Spacing", 1, 10, 3)
        self.leg_slider = self.slider("Leg Length", 1, 10, 4)
        self.head_slider = self.slider("Head Size", 1, 10, 5)
        self.eye_slider = self.slider("Eye Size", 1, 5, 2)

        self.color_combo = QtWidgets.QComboBox()
        self.color_combo.addItems([
            "Green",
            "Blue",
            "Red",
            "Rainbow"
        ])

        layout.addWidget(QtWidgets.QLabel("Color Preset"))
        layout.addWidget(self.color_combo)

        self.generate_btn = QtWidgets.QPushButton("Generate Caterpillar")
        self.random_btn = QtWidgets.QPushButton("Randomize")

        layout.addWidget(self.generate_btn)
        layout.addWidget(self.random_btn)


    def slider(self, label, minv, maxv, default):

        box = QtWidgets.QGroupBox(label)
        layout = QtWidgets.QVBoxLayout(box)

        slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        slider.setMinimum(minv)
        slider.setMaximum(maxv)
        slider.setValue(default)

        layout.addWidget(slider)
        self.layout().addWidget(box)

        return slider


    def create_connections(self):

        self.generate_btn.clicked.connect(self.generate)
        self.random_btn.clicked.connect(self.randomize)


    def randomize(self):

        for s in [
            self.segment_slider,
            self.size_slider,
            self.spacing_slider,
            self.leg_slider,
            self.head_slider,
            self.eye_slider
        ]:
            s.setValue(random.randint(s.minimum(), s.maximum()))

        self.generate()


    def generate(self):

        if cmds.objExists("Caterpillar_GRP"):
            cmds.delete("Caterpillar_GRP")

        grp = cmds.group(empty=True, name="Caterpillar_GRP")

        segments = self.segment_slider.value()
        size = self.size_slider.value() * 0.2
        spacing = self.spacing_slider.value() * 0.3
        leg_length = self.leg_slider.value() * 0.2
        head_size = self.head_slider.value() * 0.25
        eye_size = self.eye_slider.value() * 0.1

        color = self.get_color()

        for i in range(segments):

            body = cmds.polySphere(r=size)[0]
            cmds.move(i * spacing, 0, 0, body)

            self.assign_material(body, color)

            for side in [-1, 1]:
                leg = cmds.polyCylinder(r=0.05,
                                         h=leg_length)[0]

                cmds.move(i * spacing,
                          -size,
                          side * size,
                          leg)

                cmds.rotate(90, 0, 0, leg)
                cmds.parent(leg, body)

            cmds.parent(body, grp)

        head = cmds.polySphere(r=head_size)[0]
        cmds.move(-spacing, 0, 0, head)

        self.assign_material(head, color)

        for side in [-1, 1]:
            eye = cmds.polySphere(r=eye_size)[0]

            cmds.move(-spacing,
                      head_size * 0.5,
                      side * head_size * 0.5,
                      eye)

            self.assign_material(eye, (1,1,1))
            cmds.parent(eye, head)

        cmds.parent(head, grp)

        cmds.select(grp)


    def assign_material(self, obj, color):

        shader = cmds.shadingNode(
            "lambert",
            asShader=True,
            name="caterpillarMat"
        )

        sg = cmds.sets(renderable=True,
                       noSurfaceShader=True,
                       empty=True)

        cmds.connectAttr(shader + ".outColor",
                         sg + ".surfaceShader")

        cmds.setAttr(shader + ".color",
                     color[0], color[1], color[2],
                     type="double3")

        cmds.sets(obj, e=True, forceElement=sg)


    def get_color(self):

        preset = self.color_combo.currentText()

        colors = {
            "Green": (0.2, 0.8, 0.2),
            "Blue": (0.2, 0.4, 1),
            "Red": (1, 0.2, 0.2),
            "Rainbow": (
                random.random(),
                random.random(),
                random.random()
            )
        }

        return colors[preset]



def launch():

    global caterpillar_ui

    try:
        caterpillar_ui.close()
        caterpillar_ui.deleteLater()
    except:
        pass

    caterpillar_ui = CaterpillarGenerator()
    caterpillar_ui.show()