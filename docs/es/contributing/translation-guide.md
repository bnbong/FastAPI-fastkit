# Guía de traducción

Esta guía explica cómo contribuir traducciones a la documentación de FastAPI-fastkit.

## Fuente de verdad y política de traducción

> **El inglés (`en`) es la referencia canónica** de la documentación de FastAPI-fastkit. Los demás idiomas son destinos de traducción y pueden quedarse atrás respecto a una release o a páginas concretas.
>
> Si una página traducida no coincide con la página inglesa, **confía en la página inglesa** hasta que la traducción se ponga al día. Las traducciones se publican con el nivel de avance al que han llegado los colaboradores — la cobertura parcial es normal y esperada.

La página complementaria de cara al usuario es [Estado de las traducciones](../reference/translation-status.md), que muestra el grado real de traducción de cada idioma y cómo presenta MkDocs las páginas que aún no se han traducido (en resumen: se muestra la versión en inglés).

El `CHANGELOG.md` de la raíz del repositorio también se mantiene en inglés como historial de releases canónico. Si un idioma expone una página `changelog.md`, esa página debería enlazar o incluir el changelog canónico en inglés en lugar de mantener un changelog traducido aparte, a menos que la política del proyecto cambie más adelante.

Cuando contribuyas una traducción, actualiza también la tabla de la página de estado para que los usuarios puedan saber qué hay disponible sin adivinarlo a partir del selector de idiomas.

## Visión general

FastAPI-fastkit usa un sistema de traducción automatizado impulsado por IA para traducir la documentación a varios idiomas. El sistema:

- Lee la documentación fuente en inglés
- Traduce el contenido con APIs de IA (OpenAI o Anthropic)
- Guarda las traducciones en directorios por idioma
- Crea Pull Requests de GitHub para revisión

La automatización ofrece un punto de partida; sigue siendo necesaria una revisión humana antes de fusionar los cambios. Las traducciones generadas por IA deberían marcarse como "draft" en sus PRs y revisarse por una persona con dominio del idioma antes de integrarse.

## Idiomas soportados

Estos son los idiomas que el sitio de documentación **compila** actualmente. La configuración del destino de compilación por sí sola **no** significa que las páginas de ese idioma estén traducidas. Consulta [Estado de las traducciones](../reference/translation-status.md) para ver el grado real de traducción por idioma.

- 🇰🇷 Coreano (ko)
- 🇯🇵 Japonés (ja)
- 🇨🇳 Chino (zh)
- 🇪🇸 Español (es)
- 🇫🇷 Francés (fr)
- 🇩🇪 Alemán (de)

## Requisitos previos

### 1. Instalar las dependencias de traducción

```bash
# Instalar con pip
pip install openai anthropic

# O con pdm
pdm install -G translation
```

### 2. Configurar las claves de API

Necesitas una clave de API de OpenAI o de Anthropic:

```bash
# Para OpenAI
export TRANSLATION_API_KEY="sk-..."

# O para Anthropic
export TRANSLATION_API_KEY="sk-ant-..."
```

### 3. Instalar GitHub CLI (opcional)

Para crear PRs automáticamente:

```bash
# macOS
brew install gh

# Linux
curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | sudo dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | sudo tee /etc/apt/sources.list.d/github-cli.list > /dev/null
sudo apt update
sudo apt install gh

# Autenticarse
gh auth login
```

## Uso

### Con comandos Make (recomendado)

La forma más fácil de ejecutar las traducciones:

```bash
# Traducir toda la documentación a todos los idiomas
make translate

# Traducir a un idioma concreto
make translate LANG=ko

# Indicar el proveedor de API y el modelo
make translate LANG=ko PROVIDER=openai MODEL=gpt-4
make translate LANG=ko PROVIDER=github MODEL=gpt-4o-mini
```

### Usando el script directamente

#### Traducir toda la documentación

Traducir toda la documentación a todos los idiomas soportados:

```bash
python scripts/translate.py --api-provider openai
```

### Traducir a un idioma concreto

Traducir solo al coreano:

```bash
python scripts/translate.py --target-lang ko --api-provider openai
```

### Traducir archivos específicos

Traducir solo ciertos archivos de documentación:

```bash
python scripts/translate.py \
  --target-lang ko \
  --files user-guide/installation.md user-guide/quick-start.md \
  --api-provider openai
```

### Saltarse la creación del PR

Traducir sin crear un PR de GitHub:

```bash
python scripts/translate.py --target-lang ko --no-pr --api-provider openai
```

### Usar Anthropic Claude

Usa Claude de Anthropic en lugar de OpenAI:

```bash
python scripts/translate.py \
  --target-lang ko \
  --api-provider anthropic \
  --api-key "sk-ant-..."
```

## Estructura de directorios

Después de traducir, la estructura de la documentación queda así:

```
docs/
├── en/                    # Inglés (original)
│   ├── index.md
│   ├── user-guide/
│   │   ├── installation.md
│   │   ├── quick-start.md
│   │   └── ...
│   ├── tutorial/
│   └── ...
├── ko/                    # Coreano
│   ├── index.md
│   ├── user-guide/
│   └── ...
├── ja/                    # Japonés
├── zh/                    # Chino
├── es/                    # Español
├── fr/                    # Francés
├── de/                    # Alemán
├── css/                   # Recursos compartidos
├── js/                    # Recursos compartidos
└── img/                   # Recursos compartidos
```

## Flujo de trabajo de traducción

### 1. Escribir la documentación en inglés

Toda la documentación se escribe primero en inglés, en el directorio `docs/`:

```bash
# Crear nueva documentación
vim docs/user-guide/new-feature.md
```

### 2. Ejecutar la traducción

Cuando la documentación en inglés esté lista, ejecuta el script de traducción:

```bash
python scripts/translate.py --target-lang ko
```

### 3. Revisar el Pull Request

El script crea un Pull Request con las traducciones. Al revisarlo:

1. Comprueba que se mantiene el formato Markdown
2. Verifica que los términos técnicos se han tratado correctamente
3. Asegúrate de que los ejemplos de código no han cambiado
4. Busca problemas específicos del idioma

### Política de changelog

- Mantén el `CHANGELOG.md` de la raíz del repositorio en inglés.
- No abras PRs de traducción cuyo objetivo sea reescribir el historial de releases en otro idioma dentro del changelog de la raíz.
- Si un idioma necesita una página de changelog, trata `docs/<locale>/changelog.md` como una página puente o de acceso al changelog canónico en inglés.

### 4. Aprobar y mergear (para mantenedores)

Cuando la traducción esté verificada:

```bash
gh pr review <pr-number> --approve
gh pr merge <pr-number>
```

### 5. Desplegar la documentación

El sitio de documentación se reconstruye automáticamente con las nuevas traducciones.

## Configuración de la traducción

Edita `scripts/translation_config.json` para personalizar:

```json
{
  "source_language": "en",
  "target_languages": [
    {
      "code": "ko",
      "name": "Korean",
      "native_name": "한국어",
      "enabled": true
    }
  ],
  "translation_settings": {
    "default_api_provider": "openai",
    "batch_size": 5,
    "preserve_formatting": true
  },
  "github_settings": {
    "create_pr_by_default": true,
    "branch_prefix": "translation"
  }
}
```

## Buenas prácticas

### Para la documentación fuente

1. **Lenguaje claro**: escribe inglés claro y sencillo que se traduzca bien
2. **Terminología consistente**: usa términos técnicos consistentes
3. **Bloques de código correctos**: especifica siempre el lenguaje en los bloques de código
4. **Verificación de enlaces**: asegúrate de que todos los enlaces internos usan rutas relativas

### Para revisar traducciones

1. **Términos técnicos**: verifica que los términos técnicos son adecuados al idioma destino
2. **Contexto cultural**: comprueba si los ejemplos necesitan localización
3. **Formato**: asegúrate de que se conserva todo el formato Markdown
4. **Integridad del código**: verifica que los bloques de código no se han modificado

## Solución de problemas

### Límites de la API

Si llegas a los límites de la API, traduce en lotes más pequeños:

```bash
# Traducir solo la user guide
python scripts/translate.py \
  --target-lang ko \
  --files user-guide/*.md
```

### Problemas de calidad de la traducción

Si las traducciones son de baja calidad:

1. Verifica que tu clave de API es válida
2. Prueba con otro proveedor de IA
3. Divide documentos complejos en secciones más pequeñas
4. Revisa y edita la traducción manualmente

### Falla la creación del PR en GitHub

Si la creación del PR falla:

```bash
# Traducir sin PR
python scripts/translate.py --target-lang ko --no-pr

# Crear el PR manualmente
git checkout -b translation/ko
git add docs/ko/
git commit -m "Add Korean translations"
git push -u origin translation/ko
gh pr create --title "Add Korean translations"
```

## Traducción manual

También puedes traducir manualmente:

1. Copia el archivo inglés al directorio del idioma destino:
```bash
mkdir -p docs/ko/user-guide
cp docs/en/user-guide/installation.md docs/ko/user-guide/installation.md
```

2. Edita el archivo en tu editor preferido
3. Haz commit y crea un PR

## Cambio de idioma

El sitio de documentación incluye un selector de idioma en la navegación superior. Los usuarios pueden:

1. Pulsar el selector de idioma
2. Elegir su idioma preferido
3. Navegar por la documentación traducida

## Contribuir nuevos idiomas

Para añadir un idioma nuevo:

1. Edita `scripts/translation_config.json`:
```json
{
  "code": "pt",
  "name": "Portuguese",
  "native_name": "Português",
  "enabled": true
}
```

2. Actualiza `mkdocs.yml`:
```yaml
- locale: pt
  name: Português
  build: true
```

3. Ejecuta la traducción:
```bash
python scripts/translate.py --target-lang pt
```

## ¿Necesitas ayuda?

- **Issues**: reporta problemas de traducción en [GitHub Issues](https://github.com/bnbong/FastAPI-fastkit/issues)
- **Discussions**: pregunta en [GitHub Discussions](https://github.com/bnbong/FastAPI-fastkit/discussions)
- **Cómo contribuir**: consulta [CONTRIBUTING.md](https://github.com/bnbong/FastAPI-fastkit/blob/main/CONTRIBUTING.md)

## Estándares de calidad de la traducción

Todas las traducciones deben cumplir estos estándares:

- ✅ Conservar todo el formato Markdown
- ✅ No modificar los bloques de código
- ✅ Mantener la terminología técnica adecuada
- ✅ Usar gramática y ortografía correctas
- ✅ Seguir las convenciones específicas del idioma
- ✅ Comprobar que todos los enlaces funcionan

¡Gracias por contribuir a las traducciones de FastAPI-fastkit! 🌍
