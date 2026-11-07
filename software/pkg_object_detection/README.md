# Running a custom model on the OAK-D lite
- connect the OAK-D lite via USB to computer

- run the following prompts to install the luxonis stuff: 
    ```git clone --depth 1 https://github.com/luxonis/oak-examples.git

    cd oak-examples/neural-networks/generic-example

    python3 -m venv venv

    source venv/bin/activate
    
    python3 -m pip install -r requirements.txt```

- move the `best.rvc2.tar.xz` file from \Model\Konvertiertes_Model of this repo to \oak-examples\neural-networks\generic-example

- run python3 main.py --model "./best.rvc2.tar.xz" from this directory: oak-examples/neural-networks/generic-example