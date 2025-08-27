"""
Página de gerenciamento de prompts dos agentes
"""

import streamlit as st
import yaml
from pathlib import Path
from datetime import datetime

from ..components import render_alert
from ...config.settings import settings

def render():
    """Renderiza página de gerenciamento de prompts"""
    st.header("🎯 Gerenciamento de Prompts dos Agentes")
    
    st.markdown("""
    Configure os prompts que orientam o comportamento dos agentes de IA.
    Cada agente tem seu próprio conjunto de prompts para diferentes situações.
    """)
    
    # Listar arquivos de prompts disponíveis
    prompts_dir = settings.prompts_dir
    prompt_files = list(prompts_dir.glob("*.yaml"))
    
    if not prompt_files:
        render_alert("⚠️ Nenhum arquivo de prompt encontrado.", "warning")
        return
    
    # Seletor de agente
    col1, col2 = st.columns([2, 1])
    
    with col1:
        agent_names = {
            "extraction_prompts.yaml": "🔍 Agente de Extração",
            "calculation_prompts.yaml": "🧮 Agente de Cálculo",
            "report_prompts.yaml": "📊 Agente de Relatórios"
        }
        
        selected_file = st.selectbox(
            "Selecione o Agente",
            prompt_files,
            format_func=lambda x: agent_names.get(x.name, x.name)
        )
    
    with col2:
        if st.button("🔄 Recarregar", use_container_width=True):
            st.rerun()
    
    # Carregar prompts do arquivo selecionado
    if selected_file:
        load_and_edit_prompts(selected_file)

def load_and_edit_prompts(prompt_file: Path):
    """Carrega e permite edição dos prompts"""
    
    # Carregar conteúdo atual
    with open(prompt_file, 'r', encoding='utf-8') as f:
        prompts = yaml.safe_load(f) or {}
    
    st.divider()
    
    # Tabs para organizar prompts
    tabs = st.tabs(["📝 Editar Prompts", "➕ Adicionar Novo", "📋 Preview YAML"])
    
    with tabs[0]:
        # Editar prompts existentes
        st.subheader("Prompts Existentes")
        
        if not prompts:
            st.info("Nenhum prompt definido ainda.")
        else:
            # Criar um formulário para cada prompt
            for key, value in prompts.items():
                with st.expander(f"**{key}**", expanded=False):
                    # Mostrar descrição se existir
                    if isinstance(value, dict) and 'description' in value:
                        st.caption(value.get('description', ''))
                        prompt_text = value.get('prompt', '')
                    else:
                        prompt_text = value
                    
                    # Editor de texto
                    new_prompt = st.text_area(
                        "Prompt",
                        value=prompt_text,
                        height=200,
                        key=f"edit_{key}"
                    )
                    
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        if st.button(f"💾 Salvar", key=f"save_{key}"):
                            # Atualizar prompt
                            if isinstance(prompts[key], dict):
                                prompts[key]['prompt'] = new_prompt
                            else:
                                prompts[key] = new_prompt
                            
                            # Salvar arquivo
                            save_prompts(prompt_file, prompts)
                            st.success(f"✅ Prompt '{key}' salvo com sucesso!")
                            st.rerun()
                    
                    with col2:
                        if st.button(f"🗑️ Excluir", key=f"delete_{key}", type="secondary"):
                            del prompts[key]
                            save_prompts(prompt_file, prompts)
                            st.success(f"✅ Prompt '{key}' excluído!")
                            st.rerun()
    
    with tabs[1]:
        # Adicionar novo prompt
        st.subheader("Adicionar Novo Prompt")
        
        with st.form("new_prompt_form"):
            new_key = st.text_input("Nome do Prompt (ex: validate_data)")
            new_description = st.text_input("Descrição (opcional)")
            new_prompt_text = st.text_area("Texto do Prompt", height=200)
            
            submitted = st.form_submit_button("➕ Adicionar Prompt", type="primary")
            
            if submitted and new_key and new_prompt_text:
                if new_key in prompts:
                    st.error("❌ Já existe um prompt com esse nome!")
                else:
                    # Adicionar novo prompt
                    if new_description:
                        prompts[new_key] = {
                            'description': new_description,
                            'prompt': new_prompt_text
                        }
                    else:
                        prompts[new_key] = new_prompt_text
                    
                    save_prompts(prompt_file, prompts)
                    st.success(f"✅ Prompt '{new_key}' adicionado com sucesso!")
                    st.rerun()
    
    with tabs[2]:
        # Preview do arquivo YAML
        st.subheader("Preview do Arquivo YAML")
        
        yaml_content = yaml.dump(prompts, default_flow_style=False, allow_unicode=True)
        st.code(yaml_content, language='yaml')
        
        # Botão para download
        st.download_button(
            label="📥 Download YAML",
            data=yaml_content,
            file_name=f"{prompt_file.stem}_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.yaml",
            mime='text/yaml'
        )

def save_prompts(file_path: Path, prompts: dict):
    """Salva os prompts no arquivo YAML"""
    # Fazer backup antes de salvar
    backup_path = file_path.with_suffix(f'.yaml.bak')
    if file_path.exists():
        with open(file_path, 'r', encoding='utf-8') as f:
            backup_content = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(backup_content)
    
    # Salvar novo conteúdo
    with open(file_path, 'w', encoding='utf-8') as f:
        yaml.dump(prompts, f, default_flow_style=False, allow_unicode=True)
    
    # Log da alteração
    if 'prompt_changes' not in st.session_state:
        st.session_state['prompt_changes'] = []
    
    st.session_state['prompt_changes'].append({
        'timestamp': datetime.now().isoformat(),
        'file': file_path.name,
        'action': 'update'
    })
