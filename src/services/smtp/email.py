from abc import ABC, abstractclassmethod
from dataclasses import dataclass

from bs4 import BeautifulSoup
from src.services.awx.awx import Awx

from src.services.request.request import Request


@dataclass
class Email:
    subject: str
    to: str
    recipients: list
    body: BeautifulSoup
    images: dict


class TemplateBuilder(ABC):
    """Builds the email template from html file and plants the variables inside the templates"""

    vra_template = f"./src/services/smtp/templates/vra.html"
    awx_template = f"./src/services/smtp/templates/awx.html"

    @abstractclassmethod
    def build(cls, req, msg: str, task: str):
        """Build template"""


class BuildVraTemplate(TemplateBuilder):
    """Builds vra template"""

    @classmethod
    def build(cls, req: Request, msg: str, task: str):
        ## VRA EMAIL
        html_string = ""
        with open(cls.vra_template, "r") as f:
            html_string = f.read()
            html_string = str(html_string).replace("<msg>", f"<p color: #00BEA0;>{msg}</p>")
            html_string = str(html_string).replace("<task>", req.number)
            html_string = str(html_string).replace("<server>", req.servername)
            html_string = str(html_string).replace("<owner>", req.owner)
            html_string = str(html_string).replace("<domain>", req.domain)
            html_string = str(html_string).replace("<sitecode>", req.sitecode)
            html_string = str(html_string).replace("<classification>", req.classification)
            html_string = str(html_string).replace("<datadisk>", str(req.memory))
            html_string = str(html_string).replace("<bu>", req.bu)
            html_string = str(html_string).replace("<ram>", str(req.ram))
            html_string = str(html_string).replace("<cpu>", str(req.cpu))
            html_string = str(html_string).replace("<ci>", req.os)
        soup = BeautifulSoup(html_string, "lxml")
        return soup


class BuildAwxTemplate(TemplateBuilder):
    """Builds AWX template"""

    @classmethod
    def build(cls, req: Awx, msg: str, task: str):
        html_string = ""
        with open(cls.awx_template, "r") as f:
            html_string = f.read()
            html_string = str(html_string).replace("<msg>", f"<p color: #00BEA0;>{msg}</p>")
            html_string = str(html_string).replace("<server>", req.hostname)
            html_string = str(html_string).replace("<task>", task)
            html_string = str(html_string).replace("<region>", req.region)
            html_string = str(html_string).replace("<groups>", req.groups)
            html_string = str(html_string).replace("<logongroups>", req.logon_groups)
            html_string = str(html_string).replace("<job>", req.job_id)
        soup = BeautifulSoup(html_string, "lxml")
        return soup
