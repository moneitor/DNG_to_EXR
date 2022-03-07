from PySide2.QtWidgets import QApplication, QDialog, QFormLayout, QGroupBox, QHBoxLayout, QLineEdit, QPushButton, QSpinBox, QVBoxLayout, QFileDialog, QRadioButton, QProgressBar
from PySide2.QtWidgets import QListView, QAbstractItemView, QTreeView, QComboBox, QCheckBox, QDoubleSpinBox
from PySide2.QtCore import Qt
from dng_to_exr_logic import convert_all_dngs_to_exr

import os
import sys


class DNG_EXR_app(QDialog):
    def __init__(self):
        super(DNG_EXR_app, self).__init__()
        self.setWindowTitle("DNG to EXR")
        self.setMinimumSize(600, 300)
        
        self.in_path = ""
        self.out_path = ""
        
        self.highlight_mode = ""
        self.color_space = ""    
        self.use_camera_wb = 0
        self.use_gamma = 0 
        self.black = ""
        self.white = ""
        self.gamma = ""

        
        self.folders = []
        
        self.widgets()
        self.layouts()
        self.connections()
        
        
    def widgets(self):
        self.ln_file_path = QLineEdit()
        self.ln_file_path.setReadOnly(True)
        self.btn_file_search = QPushButton("Folder")
        
        
        self.grp_chks = QGroupBox("Options")
        self.chk_wb = QCheckBox("Use Camera White Balance")
        self.chk_gamma = QCheckBox("Use Gamma")   
        
        self.cmb_colorSpace = QComboBox()
        self.cmb_colorSpace.addItem("none", "0")
        self.cmb_colorSpace.addItem("sRGB", "1")
        self.cmb_colorSpace.addItem("Adobe", "2")
        self.cmb_colorSpace.addItem("Wide", "3")
        self.cmb_colorSpace.addItem("ProPhoto", "4")
        self.cmb_colorSpace.addItem("XYZ", "5")
        self.cmb_colorSpace.addItem("ACES", "6")
        self.cmb_colorSpace.setCurrentIndex(0)
        
        self.cmb_highlight = QComboBox()
        self.cmb_highlight.addItem("clip", "0")
        self.cmb_highlight.addItem("unclip", "1")
        self.cmb_highlight.addItem("blend", "2")
        self.cmb_highlight.addItem("rebuild", "3")
        self.cmb_highlight.setCurrentIndex(0)
        
        self.spn_black = QSpinBox()
        self.spn_black.setMaximum(100000)
        self.spn_black.setValue(256)
        
        self.spn_white = QSpinBox()
        self.spn_white.setMaximum(100000)
        self.spn_white.setValue(10)
        
        self.spn_gamma = QDoubleSpinBox()
        self.spn_gamma.setMaximum(10.0)
        self.spn_gamma.setValue(2.2)
        self.spn_gamma.setDisabled(True)
        
        self.pb_progress = QProgressBar()        

        self.btn_cancel = QPushButton("Cancel")
        self.btn_convert = QPushButton("Convert")
        
        
    def layouts(self):
        # INPUT PATH
        self.grp_file = QGroupBox("Input Path")
        self.lyt_file = QHBoxLayout()
        self.lyt_file.addWidget(self.ln_file_path)
        self.lyt_file.addWidget(self.btn_file_search)
        self.grp_file.setLayout(self.lyt_file)
        
        # PROGRESS BAR
        self.grp_output = QGroupBox("Progress")        
        self.lyt_output = QHBoxLayout()
        self.lyt_output.addWidget(self.pb_progress)
        self.grp_output.setLayout(self.lyt_output)
        self.grp_output.setAlignment(Qt.AlignLeft)              
        
        # OPTIONS
        self.lyt_chks = QVBoxLayout()             
        self.lyt_chks.addWidget(self.chk_wb)  
        self.lyt_chks.addWidget(self.chk_gamma)  
        self.lyt_boxes = QFormLayout()
        self.lyt_boxes.addRow("Color Space", self.cmb_colorSpace)
        self.lyt_boxes.addRow("Highlight Mode", self.cmb_highlight)
        self.lyt_boxes.addRow("Black Level", self.spn_black)
        self.lyt_boxes.addRow("Brightness", self.spn_white)
        self.lyt_boxes.addRow("Gamma", self.spn_gamma)
        self.lyt_chks.addLayout(self.lyt_boxes)
               
        self.grp_chks.setLayout(self.lyt_chks)        
        self.lyt_chks.addStretch() 
        
        # OUTPUT BUTTONS
        self.lyt_buttons = QHBoxLayout()                      
        self.lyt_buttons.addWidget(self.btn_convert)
        self.lyt_buttons.addWidget(self.btn_cancel)
        self.lyt_buttons.addStretch()

        # INITIAL LAYOUT ASSIGNMENT
        self.lyt_main = QVBoxLayout()
        self.lyt_main.addWidget(self.grp_file)
        self.lyt_main.addWidget(self.grp_output)    
        self.lyt_main.addWidget(self.grp_chks)
        self.lyt_main.addStretch()
        self.lyt_main.addLayout(self.lyt_buttons)          
        
        self.setLayout(self.lyt_main)
        
        
    def connections(self):
        self.btn_file_search.clicked.connect(self.lookup_dir)  
        self.cmb_highlight.currentIndexChanged.connect(self.update_info)   
        self.cmb_colorSpace.currentIndexChanged.connect(self.update_info) 
        self.chk_wb.toggled.connect(self.update_info)
        self.chk_gamma.toggled.connect(self.update_info)
        self.chk_gamma.toggled.connect(self.disable_parms)
        self.spn_white.valueChanged.connect(self.update_info)
        self.spn_black.valueChanged.connect(self.update_info)
        self.spn_gamma.valueChanged.connect(self.update_info)

        self.btn_convert.clicked.connect(self.dng_to_exr)
        self.btn_cancel.clicked.connect(self.close)  
    

    
    def lookup_dir(self):
        self.update_info()
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.DirectoryOnly)
        file_dialog.setOption(QFileDialog.DontUseNativeDialog, True)
        file_view = file_dialog.findChild(QListView, 'listView')

        # to make it possible to select multiple directories:
        if file_view:
            file_view.setSelectionMode(QAbstractItemView.MultiSelection)
        f_tree_view = file_dialog.findChild(QTreeView)
        if f_tree_view:
            f_tree_view.setSelectionMode(QAbstractItemView.MultiSelection)

        if file_dialog.exec():
            paths = file_dialog.selectedFiles()
            
        if len(paths) > 1:
            self.folders = paths.pop(0)
            
        self.folders = paths
        
        folder_names = [os.path.basename(name) for name in paths]
        st = "   --   ".join(f for f in folder_names)
        
        print(folder_names)
        
        filter = 'DNG File (*.DNG *.dng)'
        
        #dng_dir = QFileDialog.getExistingDirectory(self, "Select a MLV file. ", filter)      

        if len(paths) > 1:
            self.ln_file_path.setText(st)
        else:
            self.ln_file_path.setText(paths[0])       

        
    def save_dir(self):       
        
        output_dir = QFileDialog.getExistingDirectory(self, "Select Folder")        
        self.ln_output_path.setText(output_dir)
        self.folder = output_dir
        
        self.out_path = output_dir        
        
        print(output_dir)
        
        
    def update_info(self):
        self.highlight_mode = self.cmb_highlight.currentData()        
        self.color_space = self.cmb_colorSpace.currentData()
        self.use_camera_wb = (self.chk_wb.isChecked())
        self.use_gamma = (self.chk_gamma.isChecked())
        self.black = str(self.spn_black.value())
        self.white = str(self.spn_white.value())
        self.gamma = str(self.spn_gamma.value())
        
        
    def disable_parms(self):
        if self.chk_gamma.isChecked():
            self.spn_black.setDisabled(True)
            self.spn_gamma.setDisabled(False)
        else:
            self.spn_black.setDisabled(False)
            self.spn_gamma.setDisabled(True)
        
        
    def dng_to_exr(self):
        for folder in self.folders:
            output_path = folder + "_EXR"            
            
            convert_all_dngs_to_exr(folder,
                                    output_path,
                                    self.pb_progress, 
                                    self.color_space, 
                                    self.highlight_mode,
                                    self.use_camera_wb,
                                    self.use_gamma,
                                    self.black,
                                    self.white,
                                    self.gamma
                                    )
        
        
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    w = DNG_EXR_app()
    w.show()
    
    sys.exit(app.exec_())