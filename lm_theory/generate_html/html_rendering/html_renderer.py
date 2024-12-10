import os
import shutil
import warnings

from jinja2 import Environment, FileSystemLoader

from ...paper_extraction.config.config import (
    STATEMENT_TYPE_HTML_TEMPLATE_PATHS,
    STATEMENT_TYPES_METADATA,
    STATEMENT_TYPE_URL_TEMPLATE,
    PAPERS_INDEX_URL,
)

from ..html_rendering.jinja2_env_filters import (
    add_html_tabs_newlines,
    add_root,
    capitalize_first,
    code_list,
    escape_backslashes,
    link_list,
    replace_tabs_by_spaces,
    text_list,
)

from lm_theory.config.config import (
    GENERATED_HTML_DIR,
    JINJA2_TEMPLATES_ROOT,
)


class HTMLGenerator():
    def __init__(
        self, paper_database, root: str, pages_root: str,
        assets_root: str = None, generated_html_root: str = None,
        jinja2_templates_root=JINJA2_TEMPLATES_ROOT,
    ):
        self.paper_database = paper_database
        self.env = self._create_jinja2_env(jinja2_templates_root)
        self.pages_root = pages_root
        self.assets_root = assets_root
        self.root = root
        self.generated_html_root = generated_html_root or os.path.join(root, GENERATED_HTML_DIR)
        self.statement_types_data = self._statement_types_data()
        self.types_plural = [
            data['plural'] for data in STATEMENT_TYPES_METADATA.values()
        ]

    def _statement_types_data(self):
        type2data = STATEMENT_TYPES_METADATA.copy()
        for statement_type, type_data in type2data.items():
            html_url = STATEMENT_TYPE_URL_TEMPLATE.format(
                statement_type_plural=type_data['plural']
            )
            type_data['html_url'] = html_url
            type_statements = list(self.paper_database.type_statements(statement_type))
            type_data['statements'] = type_statements
        return type2data
    
    def _paper_statement_types_data(self, paper):  # TODO: merge with function above
        type2data = STATEMENT_TYPES_METADATA.copy()
        for statement_type, type_data in type2data.items():
            html_url = STATEMENT_TYPE_URL_TEMPLATE.format(
                statement_type_plural=type_data['plural']
            )
            type_data['html_url'] = html_url
            type_statements = list(paper.type_statements(statement_type))
            type_data['statements'] = type_statements
        return type2data

    def _create_jinja2_env(self, jinja2_templates_root=JINJA2_TEMPLATES_ROOT):
        env = Environment(loader=FileSystemLoader(jinja2_templates_root))
        env.filters['add_html_tabs_newlines'] = add_html_tabs_newlines
        env.filters['add_root'] = lambda s: add_root(s, self.root)
        env.filters['add_pages_root'] = lambda s: add_root(s, self.pages_root)
        env.filters['add_assets_root'] = lambda s: add_root(s, self.assets_root)
        env.filters['capitalize_first'] = capitalize_first
        env.filters['code_list'] = code_list
        env.filters['escape_backslashes'] = escape_backslashes
        env.filters['link_list'] = lambda s: link_list(s, self.pages_root)
        env.filters['replace_tabs_by_spaces'] = replace_tabs_by_spaces
        env.filters['text_list'] = text_list
        return env

    def _render_template(self, template_name, context, path):   # TODO: default None on context; TODO: add arg type definitions
        template = self.env.get_template(template_name)
        output = template.render(context)
        path = os.path.join(self.generated_html_root, path)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as f:
            f.write(output)

    # def _generate_assets_file(self):
    #     src_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'assets')
    #     dest_dir = os.path.join(self.root, 'assets')
    #     os.makedirs(os.path.dirname(dest_dir), exist_ok=True)
    #     try:
    #         shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
    #     except shutil.Error as e:
    #         warnings.warn(f'Error occurred while copying directory assets directory: {e}')
    #     except OSError as e:
    #         warnings.warn(f'OS error occurred when copying assets directory: {e}')


    def build_html_files(self):
        # self._generate_assets_file()

        self._render_template('index.html.jinja', {}, 'index.html')
        self._render_template('contact.html.jinja', {}, 'contact.html')
        self._render_template('examples.html.jinja', {}, 'examples.html')
        self._render_template('contribute.html.jinja', {}, 'contribute/index.html')
        self._render_template('add_statement.html.jinja', {}, 'contribute/add_statement.html')
        self._render_template('add_paper.html.jinja', {}, 'contribute/add_paper.html')

        self._render_template(
            'library_index.html.jinja',
            {
                'type2data': self.statement_types_data,
                'types_plural': self.types_plural,
                'papers_index_url': PAPERS_INDEX_URL,
            },
            'library/index.html'
        )

        for type_data in self.statement_types_data.values():
            context = {'type_data': type_data}
            self._render_template('statement_type_index.html.jinja', context, type_data['html_url'])

        self._render_template(
            'papers_index.html.jinja', {'papers': self.paper_database.papers}, PAPERS_INDEX_URL
        )

        for paper in self.paper_database.papers:
            type2data = self._paper_statement_types_data(paper)
            self._render_template(
                'paper.html.jinja',
                {
                    'paper': paper,
                    'type2data': type2data,
                },
                paper.html_url
            )

        for statement in self.paper_database.all_statements():
            statement_type = statement.statement_type
            template_path = STATEMENT_TYPE_HTML_TEMPLATE_PATHS[statement_type]
            paper = self.paper_database.paperid2paper(statement.paper_id)
            parent2url = {}
            parent_id = getattr(statement, 'parent_id', None)
            if parent_id:
                parent_statement = self.paper_database.statementid2statement(parent_id)
                parent2url[parent_statement.library_name] = parent_statement.html_url
            cor2url = {}
            corollary_ids = getattr(statement, 'corollary_ids', [])
            for corollary_id in corollary_ids or []:
                corollary = self.paper_database.statementid2statement(corollary_id)
                cor2url[corollary.library_name] = corollary.html_url
            self._render_template(
                template_path,
                {
                    'statement': statement,
                    'paper': paper,
                    'parent': parent2url,
                    'corollaries': cor2url,
                },
                statement.html_url
            )