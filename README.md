# StudyForge

Assistente pessoal de estudos com biblioteca Markdown, tutor com citações, pesquisa HTML temporária e seleção explícita de fontes. React/TypeScript, FastAPI, LangGraph e PostgreSQL/pgvector.

Comece pelo [guia didático da estrutura e dos fluxos](docs/guia-do-projeto.md).

A aplicação oferece **modo real**, com Gemini e Brave configurados no backend, e
**modo fixture**, com vetores/respostas de teste e páginas sintéticas sem envio
externo. O modo fixture verifica o fluxo; não demonstra qualidade semântica dos
provedores. Integrações executadas e limitações estão no estado da entrega.

Execute apenas em contêineres. Consulte [quickstart](specs/001-studyforge-mvp/quickstart.md), [estado da entrega](specs/001-studyforge-mvp/evidence/readiness.md) e [tarefas](specs/001-studyforge-mvp/tasks.md).

Acesso exclusivo em http://127.0.0.1:8000. Conversas e fontes temporárias ficam em memória até encerrar a conversa ou reiniciar. Somente uploads e fontes explicitamente selecionadas entram no banco. O gate externo G0 foi retirado: a garantia de retenção é local; APIs externas seguem as políticas dos provedores. Não coloque segredos em variáveis VITE_* ou no chat.
