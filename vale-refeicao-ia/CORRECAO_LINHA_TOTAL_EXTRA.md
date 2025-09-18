# Correção: Linha Extra de Total sem Formatação

## Problema
A planilha FORMATO_PADRAO_VR estava mostrando uma linha extra com o valor total sem formatação na linha 2, além da linha formatada corretamente na linha 1.

## Causa
O código estava:
1. Concatenando uma linha de total ao DataFrame
2. Escrevendo todo o DataFrame (incluindo a linha de total não formatada)
3. Sobrescrevendo com formatação apenas a primeira linha

## Solução Implementada

### Mudança em `excel_generator.py`

**Antes:**
```python
# Criava DataFrame com linha de total
df_com_total = pd.concat([linha_total, pd.DataFrame([{col: '' for col in df.columns}]), df], ignore_index=True)
# Escrevia todo o DataFrame
df_com_total.to_excel(writer, sheet_name=clean_name, index=False, header=False, startrow=0)
# Formatava por cima
self._format_worksheet_with_total(writer, clean_name, df_com_total, soma_total)
```

**Depois:**
```python
# Escreve apenas os dados originais a partir da linha 3
df.to_excel(writer, sheet_name=clean_name, index=False, header=False, startrow=3)
# A formatação adiciona o total na linha 0, linha vazia na 1, cabeçalhos na 2
self._format_worksheet_with_total(writer, clean_name, df, soma_total)
```

## Resultado
Agora a planilha FORMATO_PADRAO_VR tem a estrutura correta:
- **Linha 0**: Total formatado (fundo amarelo, negrito)
- **Linha 1**: Vazia
- **Linha 2**: Cabeçalhos das colunas
- **Linha 3 em diante**: Dados dos funcionários

## Como Testar
1. Reiniciar a aplicação Streamlit
2. Executar um cálculo de vale refeição
3. Verificar que a planilha tem apenas uma linha de total (formatada)

## Data: 18/09/2025
