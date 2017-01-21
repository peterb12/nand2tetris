//
//  ViewController.swift
//  Hack Assembler
//
//  Created by peterb on 12/28/16.
//  Copyright © 2016 peterb. All rights reserved.
//

import Cocoa

class ViewController: NSViewController {

    override func viewDidLoad() {
        super.viewDidLoad()
        // Do any additional setup after loading the view.
    }

    override var representedObject: Any? {
        didSet {
        // Update the view, if already loaded.
        }
    }

    @IBOutlet weak var filenameField: NSTextField!
    @IBAction func browseFile(sender: AnyObject) {
        let dialog = NSOpenPanel();
        
        dialog.title                   = "Choose a HACK asm file"
        dialog.showsResizeIndicator    = true
        dialog.showsHiddenFiles        = false
        dialog.canChooseDirectories    = true
        dialog.canCreateDirectories    = false
        dialog.allowsMultipleSelection = false
        dialog.allowedFileTypes        = ["asm"]
        
        if (dialog.runModal() == NSModalResponseOK) {
            let result = dialog.url // Pathname of the file
            
            if (result != nil) {
                let path = result!.path
                filenameField.stringValue = path
            }
        } else {
            // User clicked on "Cancel"
            return
        }
    }
    
    @IBAction func Assemble(_ sender: Any) {
        let pathString = filenameField.stringValue
        if pathString != "" {
            let path = NSURL.fileURL(withPath: pathString)
            let assembler = Assembler(asmFile: pathString)
            let machineCode = assembler.assemble(asmFile: pathString)

            let barePath = path.deletingPathExtension
            let writePath = barePath().appendingPathExtension("hack")

            //writing
            do {
                try machineCode.write(to: writePath, atomically: false, encoding: String.Encoding.utf8)
            }
            catch {/* error handling here */}
        } else {
            print("You should disable this control.")
        }
    }
    
}

