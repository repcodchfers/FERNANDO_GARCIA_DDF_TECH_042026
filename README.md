# Case Técnico Dadosfera 


**Domínio Escolhido:** Analytics para Marketplace de Food Delivery.

---

## 📅 Item 0 - Agilidade e Planejamento

Abaixo, o cronograma macro de execução do projeto seguindo as fases do Ciclo de Vida de Dados da Dadosfera e práticas de PMBOK.
```mermaid
gantt
    title Planejamento do Projeto
    dateFormat  DD-MM
    axisFormat  %d/%m

    section Engenharia
    Ingestão e Carga (Collect)      :active, p1, 30-04, 1d
    Data Quality e Catálogo         :p2, after p1, 1d
    
    section Inteligência
    Processamento LLM (GenAI)       :p3, after p2, 1d
    Modelagem e Analytics           :p4, after p3, 2d
    
    section Entrega
    Data App e Vídeo Final          :p5, after p4, 2d
## 📥 Item 1 & 2 - Base de Dados e Ingestão (Collect)
*   **Dataset Selecionado:** Swiggy Marketplace Dataset (Índia).
*   **Volume:**  197430  registros, garantindo a robustez da análise.
*   **Estratégia de Ingestão:** Utilização do módulo **Collect** da Dadosfera para carregamento de raw data (Camada Bronze).
