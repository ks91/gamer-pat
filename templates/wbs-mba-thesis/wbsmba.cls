\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{wbsmba}[2026/04/04 Waseda WBS thesis class]

\newif\ifwbs@english
\newif\ifwbs@project
\wbs@englishfalse
\wbs@projectfalse

\DeclareOption{degree-ja}{%
  \wbs@englishfalse
  \wbs@projectfalse
}
\DeclareOption{project-ja}{%
  \wbs@englishfalse
  \wbs@projecttrue
}
\DeclareOption{degree-en}{%
  \wbs@englishtrue
  \wbs@projectfalse
}
\ExecuteOptions{degree-ja}
\ProcessOptions\relax

\ifwbs@english
  \LoadClass[a4paper,11pt,openany]{report}
\else
  \LoadClass[report,paper=a4,fontsize=11pt,openany]{jlreq}
\fi

\RequirePackage{etoolbox}
\RequirePackage{geometry}
\RequirePackage{setspace}
\ifwbs@english
  \RequirePackage{graphicx}
\else
  \RequirePackage[dvipdfmx]{graphicx}
\fi
\RequirePackage{array}
\RequirePackage{booktabs}
\RequirePackage{fancyhdr}

\geometry{
  top=35mm,
  bottom=30mm,
  left=30mm,
  right=30mm,
  headheight=14pt,
  headsep=8mm,
  footskip=17.5mm,
  includeheadfoot
}

\setlength{\parindent}{2em}
\setlength{\parskip}{0pt}
\setcounter{secnumdepth}{2}
\setcounter{tocdepth}{2}

\ifwbs@english
  \doublespacing
\fi

\pagestyle{fancy}
\fancyhf{}
\fancyfoot[C]{\thepage}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

\makeatletter
\def\wbs@subtitle{}
\def\wbs@studentid{}
\def\wbs@zemi{}
\def\wbs@completiondate{}
\def\wbs@chiefexaminer{}
\def\wbs@deputyexaminerA{}
\def\wbs@deputyexaminerB{}
\def\wbs@abstractname{}
\def\wbs@bibheading{}

\ifwbs@english
  \def\wbs@thesistype{MBA Degree Thesis}
  \def\wbs@completiondate{AY 20xx}
  \def\wbs@abstractname{Summary}
  \def\wbs@bibheading{References}
  \renewcommand{\contentsname}{Table of Contents}
\else
  \ifwbs@project
    \def\wbs@thesistype{プロジェクト研究論文}
  \else
    \def\wbs@thesistype{専門職学位論文}
  \fi
  \def\wbs@completiondate{20xx年x月修了（予定）}
  \def\wbs@abstractname{概　要}
  \def\wbs@bibheading{参考文献}
  \renewcommand{\contentsname}{目次}
  \renewcommand{\listfigurename}{図目次}
  \renewcommand{\listtablename}{表目次}
\fi

\newcommand{\subtitle}[1]{\gdef\wbs@subtitle{#1}}
\newcommand{\studentid}[1]{\gdef\wbs@studentid{#1}}
\newcommand{\zemi}[1]{\gdef\wbs@zemi{#1}}
\newcommand{\completiondate}[1]{\gdef\wbs@completiondate{#1}}
\newcommand{\chiefexaminer}[1]{\gdef\wbs@chiefexaminer{#1}}
\newcommand{\deputyexaminer}[1]{\gdef\wbs@deputyexaminerA{#1}}
\newcommand{\seconddeputyexaminer}[1]{\gdef\wbs@deputyexaminerB{#1}}

\newcommand{\wbs@printdeputies}{%
  \ifstrempty{\wbs@deputyexaminerA}{}{%
    \ifwbs@english
      D.E. \wbs@deputyexaminerA%
    \else
      副査：\wbs@deputyexaminerA%
    \fi
  }%
  \ifstrempty{\wbs@deputyexaminerB}{}{%
    \ifwbs@english
      \hspace{1.5em}D.E. \wbs@deputyexaminerB%
    \else
      \hspace{1.5em}副査：\wbs@deputyexaminerB%
    \fi
  }%
}

\newcommand{\makewbscoversheet}{%
  \begin{titlepage}
    \thispagestyle{empty}
    \ifwbs@english
      \begin{flushright}
        \large \wbs@completiondate
      \end{flushright}
      \vspace*{2.5cm}
      \begin{center}
        {\LARGE\bfseries \MakeUppercase{\@title}\par}
        \ifstrempty{\wbs@subtitle}{}{\vspace{0.8cm}{\Large \wbs@subtitle\par}}
        \vspace{1.6cm}
        {\large \wbs@studentid\quad \@author\par}
        \vspace{0.4cm}
        {\large \wbs@zemi\par}
        \vspace{0.8cm}
        \ifstrempty{\wbs@chiefexaminer}{}{{\large C.E. \wbs@chiefexaminer\par}}
        \ifstrempty{\wbs@deputyexaminerA}{}{\vspace{0.3cm}{\large \wbs@printdeputies\par}}
      \end{center}
      \vfill
    \else
      \begin{flushright}
        〈\wbs@thesistype〉\hspace{2em}\wbs@completiondate
      \end{flushright}
      \vspace*{2.2cm}
      \begin{center}
        {\Huge\bfseries \@title\par}
        \ifstrempty{\wbs@subtitle}{}{\vspace{0.8cm}{\Large \wbs@subtitle\par}}
      \end{center}
      \vspace{1.8cm}
      {\large 学籍番号：\wbs@studentid\hfill 氏名：\@author\par}
      \vspace{0.6cm}
      {\large ゼミ名称：\wbs@zemi\par}
      \vspace{0.6cm}
      \ifstrempty{\wbs@chiefexaminer}{}{{\large 主査：\wbs@chiefexaminer\par}}
      \ifstrempty{\wbs@deputyexaminerA}{}{\vspace{0.3cm}{\large \wbs@printdeputies\par}}
      \vfill
    \fi
  \end{titlepage}
}

\newenvironment{abstractpage}{%
  \cleardoublepage
  \thispagestyle{empty}
  \null\vspace*{1.5cm}
  \begin{center}
    {\Large\bfseries \wbs@abstractname\par}
  \end{center}
  \vspace{1.2cm}
}{%
  \par
  \clearpage
}

\newcommand{\wbsfrontmatter}{%
  \pagenumbering{roman}
  \setcounter{page}{1}
}

\newcommand{\wbsmainmatter}{%
  \clearpage
  \pagenumbering{arabic}
  \setcounter{page}{1}
}

\AtBeginDocument{%
  \@ifundefined{bibname}
    {\@ifundefined{refname}{}{\renewcommand{\refname}{\wbs@bibheading}}}
    {\renewcommand{\bibname}{\wbs@bibheading}}%
  \ifwbs@english\else
    \def\@cite#1#2{(#1\if@tempswa, #2\fi)}%
  \fi
}

\renewcommand{\maketitle}{\makewbscoversheet}

\makeatother
