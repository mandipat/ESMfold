# This is app is created by Chanin Nantasenamat (Data Professor) https://youtube.com/dataprofessor
# Credit: This app is inspired by https://huggingface.co/spaces/osanseviero/esmfold

import streamlit as st
from stmol import showmol
import py3Dmol
import requests
import biotite.structure.io as bsio

#st.set_page_config(layout = 'wide')
st.sidebar.title('🎈 ESMFold')
st.sidebar.write('[*ESMFold*](https://esmatlas.com/about) is an end-to-end single sequence protein structure predictor based on the ESM-2 language model. For more information, read the [research article](https://www.biorxiv.org/content/10.1101/2022.07.20.500902v2) and the [news article](https://www.nature.com/articles/d41586-022-03539-1) published in *Nature*.')


style_options = ["cartoon", "stick", "sphere", "line"]
selected_style = st.selectbox("Select style", style_options, index=0)
bg_color = st.color_picker("Background Color", "#FFFFFF")
spin = st.checkbox("Spin", value=True)

def render_mol(pdb_string):
    view = py3Dmol.view()
    view.addModel(pdb_string, 'pdb')
    view.setStyle({selected_style: {'color': 'spectrum'}})
    view.setBackgroundColor(bg_color)
    view.zoomTo()
    view.spin(spin)
    showmol(view, height=500, width=800)

# Protein sequence input
DEFAULT_SEQ = "MGSSHHHHHHSSGLVPRGSHMRGPNPTAASLEASAGPFTVRSFTVSRPSGYGAGTVYYPTNAGGTVGAIAIVPGYTARQSSIKWWGPRLASHGFVVITIDTNSTLDQPSSRSSQQMAALRQVASLNGTSSSPIYGKVDTARMGVMGWSMGGGGSLISAANNPSLKAAAPQAPWDSSTNFSSVTVPTLIFACENDSIAPVNSSALPIYDSMSRNAKQFLEINGGSHSCANSGNSNQALIGKKGVAWMKRFMDNDTRYSTFACENPNSTRVSDFRTANCSLEDPAANKARKEAELAAATAEQ"
txt = st.sidebar.text_area('Input sequence', DEFAULT_SEQ, height=275)

# ESMfold
def update(sequence=txt):
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
    }
    response = requests.post('https://api.esmatlas.com/foldSequence/v1/pdb/', headers=headers, data=sequence)
    name = sequence[:3] + sequence[-3:]
    pdb_string = response.content.decode('utf-8')

    with open('predicted.pdb', 'w') as f:
        f.write(pdb_string)

    struct = bsio.load_structure('predicted.pdb', extra_fields=["b_factor"])
    b_value = round(struct.b_factor.mean(), 4)

    # Display protein structure
    st.subheader('Visualization of predicted protein structure')
    render_mol(pdb_string)

    # plDDT value is stored in the B-factor field
    st.subheader('plDDT')
    st.write('plDDT is a per-residue estimate of the confidence in prediction on a scale from 0-100.')
    st.info(f'plDDT: {b_value}')

    st.download_button(
        label="Download PDB",
        data=pdb_string,
        file_name='predicted.pdb',
        mime='text/plain',
    )

predict = st.sidebar.button('Predict', on_click=update)


if not predict:
    st.warning('👈 Enter protein sequence data!')
