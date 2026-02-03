import re
import unicodedata
import os
from werkzeug.utils import secure_filename


class CVParser:
    """Parser de CVs que extrae información relevante de archivos PDF y DOCX."""

    # Tecnologías reconocidas
    TECNOLOGIAS = {
        'PYTHON', 'JAVA', 'JAVASCRIPT', 'JS', 'TYPESCRIPT', 'TS',
        'C', 'C++', 'CPP', 'C#', 'CSHARP', 'GO', 'GOLANG', 'RUST', 'RUBY',
        'PHP', 'SWIFT', 'KOTLIN', 'SCALA', 'R', 'MATLAB',
        'SQL', 'MYSQL', 'POSTGRESQL', 'POSTGRES', 'MONGODB', 'REDIS',
        'ORACLE', 'SQLSERVER', 'SQLITE', 'CASSANDRA', 'DYNAMODB',
        'HTML', 'CSS', 'SASS', 'LESS',
        'REACT', 'REACTJS', 'ANGULAR', 'VUE', 'VUEJS', 'SVELTE',
        'NODEJS', 'NODE', 'EXPRESS', 'DJANGO', 'FLASK', 'FASTAPI',
        'SPRING', 'SPRINGBOOT', 'HIBERNATE', 'LARAVEL', 'RAILS',
        'DOCKER', 'KUBERNETES', 'K8S', 'AWS', 'AZURE', 'GCP',
        'JENKINS', 'GITLAB', 'GITHUB', 'TERRAFORM', 'ANSIBLE',
        'LINUX', 'BASH', 'GIT', 'REST', 'GRAPHQL', 'GRPC',
        'TENSORFLOW', 'PYTORCH', 'KERAS', 'PANDAS', 'NUMPY',
        'EXCEL', 'POWER BI', 'TABLEAU', 'SAP', 'SALESFORCE',
        'FIGMA', 'SKETCH', 'ADOBE', 'PHOTOSHOP', 'ILLUSTRATOR',
        'JIRA', 'CONFLUENCE', 'TRELLO', 'NOTION', 'SLACK',
        'SCRUM', 'AGILE', 'KANBAN', 'DEVOPS', 'CI/CD', 'CICD',
    }

    # Patrones para títulos universitarios
    TITULOS_PATTERNS = [
        r'licenciad[oa]',
        r'ingenier[oa]',
        r'master',
        r'maestr[íi]a',
        r'doctorado',
        r'phd',
        r'mba',
        r'bachelor',
        r'degree',
        r't[ée]cnico superior',
        r'universidad',
        r'facultad',
        r'graduad[oa]',
        r'egresad[oa]',
        r'carrera universitaria',
        r'título universitario',
        r'titulo universitario',
    ]

    # Niveles de inglés
    NIVEL_INGLES_PATTERNS = {
        'FLUIDO': [r'ingl[ée]s\s*(nativo|fluido|fluent|native|c2|proficient)', r'(fluent|native|bilingual)\s*english'],
        'AVANZADO': [r'ingl[ée]s\s*(avanzado|advanced|c1|upper)', r'(advanced|upper)\s*english'],
        'INTERMEDIO': [r'ingl[ée]s\s*(intermedio|intermediate|b1|b2|medium)', r'(intermediate|medium)\s*english'],
        'BASICO': [r'ingl[ée]s\s*(b[áa]sico|basic|a1|a2|elementary)', r'(basic|elementary)\s*english'],
    }

    @staticmethod
    def normalizar_texto(texto):
        """Normaliza texto removiendo acentos y convirtiendo a minúsculas."""
        if not texto:
            return ''
        # Normalizar unicode y remover acentos
        texto = unicodedata.normalize('NFD', texto)
        texto = ''.join(c for c in texto if unicodedata.category(c) != 'Mn')
        return texto.lower()

    @staticmethod
    def extraer_texto_pdf(filepath):
        """Extrae texto de un archivo PDF."""
        try:
            import pdfplumber
            texto = ''
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        texto += page_text + '\n'
            return texto
        except Exception as e:
            print(f"Error extrayendo PDF: {e}")
            return ''

    @staticmethod
    def extraer_texto_docx(filepath):
        """Extrae texto de un archivo DOCX."""
        try:
            from docx import Document
            doc = Document(filepath)
            texto = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return texto
        except Exception as e:
            print(f"Error extrayendo DOCX: {e}")
            return ''

    @classmethod
    def extraer_texto(cls, filepath):
        """Extrae texto de un archivo según su extensión."""
        ext = os.path.splitext(filepath)[1].lower()
        if ext == '.pdf':
            return cls.extraer_texto_pdf(filepath)
        elif ext in ['.docx', '.doc']:
            return cls.extraer_texto_docx(filepath)
        else:
            # Intentar leer como texto plano
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return f.read()
            except:
                return ''

    @classmethod
    def extraer_experiencia(cls, texto):
        """Extrae años de experiencia del texto."""
        texto_norm = cls.normalizar_texto(texto)

        patterns = [
            r'(\d+)\+?\s*(?:años|anos|years)\s*(?:de\s*)?(?:experiencia|experience)',
            r'experiencia\s*(?:de\s*)?(\d+)\+?\s*(?:años|anos|years)',
            r'(\d+)\+?\s*(?:años|anos|years)\s*(?:trabajando|working)',
            r'mas de\s*(\d+)\s*(?:años|anos)',
            r'more than\s*(\d+)\s*years',
        ]

        max_exp = 0
        for pattern in patterns:
            matches = re.findall(pattern, texto_norm)
            for match in matches:
                try:
                    exp = int(match)
                    if exp > max_exp and exp < 50:  # sanity check
                        max_exp = exp
                except:
                    pass

        return max_exp if max_exp > 0 else None

    @classmethod
    def extraer_tecnologias(cls, texto):
        """Extrae tecnologías mencionadas en el texto."""
        texto_upper = texto.upper()
        encontradas = set()

        for tech in cls.TECNOLOGIAS:
            # Buscar la tecnología como palabra completa
            pattern = r'\b' + re.escape(tech) + r'\b'
            if re.search(pattern, texto_upper):
                # Normalizar algunas variantes
                if tech in ['JS', 'JAVASCRIPT']:
                    encontradas.add('JAVASCRIPT')
                elif tech in ['TS', 'TYPESCRIPT']:
                    encontradas.add('TYPESCRIPT')
                elif tech in ['NODEJS', 'NODE']:
                    encontradas.add('NODE.JS')
                elif tech in ['REACTJS', 'REACT']:
                    encontradas.add('REACT')
                elif tech in ['VUEJS', 'VUE']:
                    encontradas.add('VUE')
                elif tech in ['POSTGRES', 'POSTGRESQL']:
                    encontradas.add('POSTGRESQL')
                elif tech in ['K8S', 'KUBERNETES']:
                    encontradas.add('KUBERNETES')
                elif tech in ['CPP', 'C++']:
                    encontradas.add('C++')
                elif tech in ['CSHARP', 'C#']:
                    encontradas.add('C#')
                elif tech in ['GOLANG', 'GO']:
                    encontradas.add('GO')
                elif tech in ['CICD', 'CI/CD']:
                    encontradas.add('CI/CD')
                else:
                    encontradas.add(tech)

        return sorted(list(encontradas))

    @classmethod
    def extraer_nivel_ingles(cls, texto):
        """Extrae el nivel de inglés del texto."""
        texto_norm = cls.normalizar_texto(texto)

        # Buscar de mayor a menor nivel
        for nivel, patterns in cls.NIVEL_INGLES_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, texto_norm):
                    return nivel

        # Si menciona inglés pero no especifica nivel
        if re.search(r'\bingl[ée]s\b|\benglish\b', texto_norm):
            return 'BASICO'

        return None

    @classmethod
    def tiene_titulo_universitario(cls, texto):
        """Detecta si el CV menciona título universitario."""
        texto_norm = cls.normalizar_texto(texto)

        for pattern in cls.TITULOS_PATTERNS:
            if re.search(pattern, texto_norm):
                return True

        return False

    @classmethod
    def parsear(cls, filepath=None, texto=None):
        """
        Parsea un CV y extrae información estructurada.

        Args:
            filepath: Ruta al archivo del CV
            texto: Texto del CV (si ya fue extraído)

        Returns:
            dict con experiencia, tecnologias, nivel_ingles, tiene_titulo
        """
        if texto is None and filepath:
            texto = cls.extraer_texto(filepath)

        if not texto:
            return {
                'experiencia': None,
                'tecnologias': [],
                'nivel_ingles': None,
                'tiene_titulo': False,
                'texto_raw': ''
            }

        return {
            'experiencia': cls.extraer_experiencia(texto),
            'tecnologias': cls.extraer_tecnologias(texto),
            'nivel_ingles': cls.extraer_nivel_ingles(texto),
            'tiene_titulo': cls.tiene_titulo_universitario(texto),
            'texto_raw': texto
        }
