# Correção: Duplicação de Excel e Linha de Total

## Problemas Corrigidos

### 1. Geração Duplicada de Planilhas Excel

**Problema**: A aplicação estava gerando duas planilhas Excel com nomes diferentes quando executava o cálculo de vale refeição.

**Causa**: 
- O cálculo de vale refeição gerava automaticamente um Excel
- A síntese final também tentava gerar outro Excel
- Não havia verificação para evitar duplicação

**Solução Implementada**:
```python
# Em database_viewer.py, linha 1755
excel_already_generated = any(
    step.get('result', {}).get('excel_generated', False) or 
    step.get('action', '') == 'Exportação Excel'
    for step in analysis_steps
)

if final_synthesis.get('generate_excel', False) and not excel_already_generated:
    # Gerar Excel apenas se ainda não foi gerado
```

### 2. Duas Linhas de Total na Planilha

**Problema**: A planilha FORMATO_PADRAO_VR estava mostrando duas linhas de total - uma sem formatação e outra com formatação.

**Causa**: 
- O DataFrame era escrito com `to_excel(..., header=True)` que adiciona cabeçalhos automaticamente
- A função `_format_worksheet_with_total` escrevia os cabeçalhos novamente

**Solução Implementada**:
```python
# Em excel_generator.py, linha 98
# Mudou de:
df_com_total.to_excel(writer, sheet_name=clean_name, index=False, startrow=0)

# Para:
df_com_total.to_excel(writer, sheet_name=clean_name, index=False, header=False, startrow=0)
```

### 3. Método de Download Simplificado

**Problema**: O método base64 com link HTML poderia causar comportamentos inesperados em alguns navegadores.

**Solução**: Substituído por `st.download_button` padrão do Streamlit:
```python
st.download_button(
    label=f"📥 Baixar Planilha Excel ({len(excel_data)/1024:.1f} KB)",
    data=excel_data,
    file_name=filename,
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    key=f"excel_download_{iteration}_{int(datetime.now().timestamp())}"
)
```

## Como Testar

1. Reinicie a aplicação Streamlit (Ctrl+C e executar novamente)
2. Execute um cálculo de vale refeição
3. Verifique:
   - Apenas uma planilha deve ser gerada
   - A planilha FORMATO_PADRAO_VR deve ter apenas uma linha de total (formatada com fundo amarelo)
   - O download deve ocorrer normalmente ao clicar no botão

## Arquivos Modificados

1. `src/ui/pages/database_viewer.py`:
   - Adicionada verificação para evitar duplicação de Excel
   - Simplificado método de download
   
2. `src/utils/excel_generator.py`:
   - Corrigido para escrever sem headers duplicados

## Data: 18/09/2025
