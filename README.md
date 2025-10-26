# Pycyphal_Test1

# Clone Public Regulated Data types
git clone https://github.com/OpenCyphal/public_regulated_data_types ~/.cyphal/public_regulated_data_types

# Compile the UAVCAN namespace
python3 -m nunavut \
  --target-language=py \
  --outdir ~/.cyphal/dsdl \
  ~/.cyphal/public_regulated_data_types/uavcan

# Compile the REG namespace (it references UAVCAN)
python3 -m nunavut \
  --target-language=py \
  --outdir ~/.cyphal/dsdl \
  --lookup-dir ~/.cyphal/public_regulated_data_types/uavcan \
  ~/.cyphal/public_regulated_data_types/reg


# Export the path
export PYTHONPATH="$HOME/.cyphal/dsdl:$PYTHONPATH"
python3 -c "import uavcan; import reg; print('✅ DSDL OK')"

# Yakut Settings
nano ~/.yakut.yaml

transport:
  can:
    media: socketcan
    interface: can0
    mtu: 8
    local_node_id: 127

# Export the path & reload
export PYTHONPATH="$HOME/.cyphal/dsdl:$PYTHONPATH"
source ~/.bashrc
python3 -c "import uavcan, reg; print('✅ DSDL OK ->', uavcan.__path__)"

# activate venv
cd ~/yc
source bin/activate

