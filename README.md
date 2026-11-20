# Central de Gestão de Serviços

Sistema desktop desenvolvido em **Python** para automatizar e otimizar os processos operacionais da empresa DDcontrol, centralizando a geração de Ordens de Serviço (OS), recibos e certificados a partir de dados extraídos do sistema Benu.

O projeto surgiu da necessidade de reduzir tarefas manuais, agilizar a emissão de documentos e padronizar os processos internos, oferecendo uma interface gráfica intuitiva para facilitar a utilização pelos colaboradores.

## Funcionalidades

- **Geração de Ordem de Serviço:** consulta os dados do cliente no Benu e gera automaticamente a OS, incluindo o recibo quando necessário.
- **Processamento em lote (Esteira de OS):** importa códigos de clientes de uma planilha Excel e processa múltiplas Ordens de Serviço automaticamente.
- **Geração de recibos:** extrai os dados financeiros do cliente e gera recibos utilizando os modelos personalizados da empresa.
- **Geração de certificados:** coleta os dados cadastrais e informações do serviço para preencher automaticamente os modelos de certificados.
- **Integração com o Benu:** automatiza a consulta e extração de informações diretamente do sistema.
- **Acompanhamento de processos:** apresenta mensagens de progresso e informações sobre cada etapa da execução.
- **Execução em threads:** permite realizar operações demoradas sem bloquear a interface gráfica.

## Tecnologias e recursos

- Python
- Selenium
- Automação de processos (RPA)
- Integração com sistema web
- Manipulação de arquivos Excel
- Geração automatizada de documentos
- Interface gráfica
- Threads e processamento assíncrono

## Objetivo

Demonstrar a aplicação de Python na resolução de problemas reais de negócios, utilizando automação para reduzir atividades repetitivas, melhorar a produtividade e tornar os processos operacionais mais eficientes.

---

**Desenvolvedor:** Marcos Martins da Silva  
**Projeto:** Central de Gestão de Serviços  
**Versão documentada:** 4.0