% LaTeX Tempkate for thesises for the research group CSSSA - Computational Social Science & Systems Analysis 
% Author: Janina Lütke Stockdiek (janina.lsd@uni-muenster.de) 
%
% Terms of use: Under no condition, do NOT change this file!
% If additional packages are required, add them in the "main.tex"-file in the preamble. If problems occur, contact the author
\def\fileversion{1.0}
% 1.0 Initial release: 
\def\filedate{2024/02/01}

% ============================================================

% _______________ Class Definition _______________

\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{settings/csssa-thesis}

% Conditional commands
\RequirePackage{kvoptions}
\RequirePackage{ifthen}

% Namespacing
\SetupKeyvalOptions{
	family=csssa,
	prefix=csssa@
}

% Set English as default language
\DeclareStringOption[]{language}[english]

% Set Master Thesis as default document type
\DeclareStringOption[]{thesis}[master]

% Set supervisor ≠ professor as default supervisor option
\DeclareStringOption[]{supervisor}[supervisor]

% Option in case of multiple authors
\DeclareBoolOption{multiauthor}

% Process options
\ProcessKeyvalOptions*

\LoadClass[a4paper,9pt,twocolumn]{extarticle}

% _______________ Packages _______________

% Set margings and spaces
\RequirePackage[a4paper,left=2cm, top=2.2cm, bottom=2cm, right=2cm, includefoot, heightrounded]{geometry}

% General language and symbol settings
\RequirePackage[utf8]{inputenc}
\RequirePackage[T1]{fontenc}

% Nice Tables 
\RequirePackage{booktabs}

% Add dummy text
\RequirePackage{lipsum}

% Images & Drawing
\RequirePackage{graphicx}
\RequirePackage{xcolor}
\RequirePackage{tikz}

% Math and Symbols
\RequirePackage{amsmath}
\RequirePackage{amssymb}
\RequirePackage{eurosym}
\RequirePackage{MnSymbol,wasysym}

% Listings
\RequirePackage{algorithm}
\RequirePackage[noend]{algpseudocode}
\RequirePackage{algorithmicx}
\RequirePackage{minted}
\usemintedstyle{tango}
\newcounter{lstlisting}

% Figures and Floats
\RequirePackage{float}
\RequirePackage{caption}
\RequirePackage{subcaption}

% Change shape of enumerate and itemize environments
\RequirePackage{enumitem}

% Break URLs at hyphen and add options for customizing links and references
\RequirePackage[hyphens]{url}
\RequirePackage{hyperref}
\hypersetup{colorlinks=true, linkcolor=black, anchorcolor=black, citecolor=black, menucolor=black, urlcolor=black}

% Headers and Footers 
\RequirePackage{fancyhdr}
% Line spacing options 
\RequirePackage{setspace}
\RequirePackage{etoolbox}
% Citation style
\RequirePackage[backend=biber, style=ieee,maxcitenames=3,hyperref=true, natbib=true]{biblatex}
\addbibresource{library.bib}

% Macro for creating options
\newcommand{\csssa@new@option}{\@ifstar{\csssa@new@option@star}{\csssa@new@option@nostar}}


\renewcommand{\maketitle}{
    \setcounter{page}{1}
    \twocolumn[{%
    \begin{center}%
    \let \footnote \thanks
    {\Huge \@title \par}%
    \vspace{12mm}
    \end{center}
    }]
}

\fancypagestyle{firstpage}{%
  \fancyhf{}%
}

\newcommand{\declarationTool}[1]{\def\@declarationTool{#1}}


\newcommand{\backmatter}{
    \clearpage
    \newpage
    \onecolumn 
    \onehalfspacing
    \declaration
    \noindent \@declarationTool
    \consent
    \setlength{\parskip}{6pt}%
    \thispagestyle{empty}
    \clearpage
}
    
% Options for different languages
\ifthenelse{\equal{\csssa@language}{english}}{
	\RequirePackage[ngerman,english]{babel}
	\RequirePackage[en-GB,showdow]{datetime2}
    \RequirePackage{csquotes} % Language-dependent quotation marks.
    

    \renewenvironment{abstract}{
        \subsection*{\centering Abstract}
        \small 
        \begin{spacing}{1.1}
        }{\end{spacing}
        \vspace{- 1mm}
        }

    \defbibheading{header}[References]{%
        \subsection*{#1}%
  }
    \ifthenelse{\equal{\csssa@supervisor}{supervisor}}{
        \newcommand{\maketitlepage}{
            \thispagestyle{empty}
            \begin{minipage}{\textwidth}
            \begin{center}
            \includegraphics[width=.3\textwidth]{settings/logos/UniMuenster_Schloss_2023_RGB.png}
        
            \vspace{5mm}
            {\textsc{\Huge University of M\"unster}}\par
            \vspace{2mm}
            {\scshape\LARGE Department of Information Systems}\par
            \vspace{1cm}
            {\textcolor{gray}{\rule{0.9\textwidth}{0.5mm}}}
            \vspace*{0.5cm}
            \begin{center}
                \begin{minipage}{0.9\textwidth}
                    \begin{center}
                        {\Huge\parindent0pt
                        \begin{spacing}{1.13}
                            \@title
                        \end{spacing}}\par
                    \end{center}
                \end{minipage}
            \end{center}
            \vspace*{-0.3cm}
            {\textcolor{gray}{\rule{0.9\textwidth}{0.5mm}}}\par
            \vspace{20mm}
            \begin{center}
                \begin{minipage}{0.9\textwidth}
                    \begin{center}
                        \Huge \@thesistype
                    \end{center}
                \end{minipage}
            \end{center}
            \vspace{4mm}
            {\Large submitted on \@date\,\,by}\par
            \vspace{20mm}
            {\Huge{\@author}}\par
            \vspace{2mm}
            {\LARGE{\@id}} \\ 
            \vspace{2mm}
            {\LARGE{\@email}} \\ 
            \vspace{55mm} 
            \begin{minipage}{0.8\textwidth}
                \centering
                \Large{\@professor\, and \@supervisor} \\ \vspace{2mm}
                {\LARGE\textsc{Research Group \\
                Computational Social Science \& Systems Analytics}}
            \end{minipage}
            \end{center}
            \end{minipage}
            \clearpage   
        } 
    }{
       \newcommand{\maketitlepage}{
            \thispagestyle{empty}
            \begin{minipage}{\textwidth}
            \begin{center}
            \includegraphics[width=.3\textwidth]{settings/logos/UniMuenster_Schloss_2023_RGB.png}
        
            \vspace{5mm}
            {\textsc{\Huge University of M\"unster}}\par
            \vspace{2mm}
            {\scshape\LARGE Department of Information Systems}\par
            \vspace{1cm}
            {\textcolor{gray}{\rule{0.9\textwidth}{0.5mm}}}
            \vspace*{0.5cm}
            \begin{center}
                \begin{minipage}{0.9\textwidth}
                    \begin{center}
                        {\Huge\parindent0pt
                        \begin{spacing}{1.13}
                            \@title
                        \end{spacing}}\par
                    \end{center}
                \end{minipage}
            \end{center}
            \vspace*{-0.3cm}
            {\textcolor{gray}{\rule{0.9\textwidth}{0.5mm}}}\par
            \vspace{20mm}
            \begin{center}
                \begin{minipage}{0.9\textwidth}
                    \begin{center}
                        \Huge \@thesistype
                    \end{center}
                \end{minipage}
            \end{center}
            \vspace{4mm}
            {\Large submitted on \@date\,\,by}\par
            \vspace{20mm}
            {\Huge{\@author}}\par
            \vspace{2mm}
            {\LARGE{\@id}} \\ 
            \vspace{2mm}
            {\LARGE{\@email}} \\ 
            \vspace{55mm} 
            \begin{minipage}{0.8\textwidth}
                \centering
                \Large{\@supervisor} \\ \vspace{2mm}
                {\LARGE\textsc{Research Group \\
                Computational Social Science \& Systems Analytics}}
            \end{minipage}
            \end{center}
            \end{minipage}
            \clearpage   
        }
    }
    
    \newcommand{\declaration}{
        \Large 
        \newpage
        \thispagestyle{empty}
        \section*{\LARGE Declaration of Authorship}
            \noindent  \ifcsssa@multiauthor We hereby declare that, to the best of our knowledge and belief, this thesis titled \textit{\@title} is our own, independent work. Below, we confirm that each significant contribution to and quotation in this thesis that originates from the work or works of others is indicated by proper use of citation and references; this also holds for tables and graphical works.
            \noindent  \else I hereby declare that, to the best of my knowledge and belief, this thesis titled \textit{\@title} is my own, independent work. Below, I confirm that each significant contribution to and quotation in this thesis that originates from the work or works of others is indicated by proper use of citation and references; this also holds for tables and graphical works.

    }
    
    \newcommand{\consent}{
        \Large 
        \section*{\LARGE Consent Form}\par
        \textbf{Name:} \@author \\
        \textbf{Title of Thesis:} \@title
    
        \noindent  \textbf{What is plagiarism?} Plagiarism is defined as submitting someone else’s work or ideas as your own without a complete indication of the source. It is hereby irrelevant whether the work of others is copied word by word without acknowledgment of the source, text structures (e.g. line of argumentation or outline) are borrowed or texts are translated from a foreign language.\par
        \noindent  \textbf{Use of plagiarism detection software.} The examination office uses plagiarism software to check each submitted bachelor and master thesis for plagiarism. For that purpose the thesis is electronically forwarded to a software service provider where the software checks for potential matches between the submitted work and work from other sources. For future comparisons with other theses, your thesis will be permanently stored in a database. Only the School of Business and Economics of the University of Münster is allowed to access your stored thesis. The student agrees that his or her thesis may be stored and reproduced only for the purpose of plagiarism assessment. The first examiner of the thesis will be advised on the outcome of the plagiarism assessment.\par
        \noindent  \textbf{Sanctions.} Each case of plagiarism constitutes an attempt to deceive in terms of the examination regulations and will lead to the thesis being graded as “failed”. This will be communicated to the examination office where your case will be documented. In the event of a serious case of deception the examinee can be generally excluded from any further examination. This can lead to the exmatriculation of the student. Even after completion of the examination procedure and graduation from university, plagiarism can result in a withdrawal of the awarded academic degree.\par
        \noindent  \ifcsssa@multiauthor We confirm that we have read and understood the information in this document. We agree to the outlined procedure for plagiarism assessment and potential sanctioning.
        \noindent  \else I confirm that I have read and understood the information in this document. I agree to the outlined procedure for plagiarism assessment and potential sanctioning.
        \fi\par
        \noindent  \signatures{Signatures}
    }

}{\ifthenelse{\equal{\csssa@language}{german}}{
	\RequirePackage[english,ngerman]{babel}
    \frenchspacing
    \RequirePackage[german,showdow]{datetime2}
	\RequirePackage{icomma}
    \RequirePackage[autostyle,german=quotes]{csquotes} % Language-dependent quotation marks.
        
    \defbibheading{header}[Literatur]{%
    \subsection*{#1}%
  }

    \renewenvironment{abstract}{
        \subsection*{\centering Kurzfassung}
        \small 
        \begin{spacing}{1.1}
        }{\end{spacing}
        \vspace{- 1mm}
    }

    \ifthenelse{\equal{\csssa@supervisor}{supervisor}}{
        \newcommand{\maketitlepage}{
            \thispagestyle{empty}
            \begin{minipage}{\textwidth}
            \begin{center}
            \includegraphics[width=.3\textwidth]{settings/logos/UniMuenster_Schloss_2023_RGB.png}
        
            \vspace{5mm}
            {\textsc{\Huge Universität Münster}}\par
            \vspace{2mm}
            {\scshape\LARGE Institut für Wirtschaftsinformatik}\par
            \vspace{1cm}
            {\textcolor{gray}{\rule{0.9\textwidth}{0.5mm}}}
            \vspace*{0.5cm}
            \begin{center}
                \begin{minipage}{0.9\textwidth}
                    \begin{center}
                        {\Huge\parindent0pt
                        \begin{spacing}{1.13}
                            \@title
                        \end{spacing}}\par
                    \end{center}
                \end{minipage}
            \end{center}
            \vspace*{-0.3cm}
            {\textcolor{gray}{\rule{0.9\textwidth}{0.5mm}}}\par
            \vspace{20mm}
            \begin{center}
                \begin{minipage}{0.9\textwidth}
                    \begin{center}
                        \Huge \@thesistype
                    \end{center}
                \end{minipage}
            \end{center}
            \vspace{4mm}
            {\Large eingereicht am \@date\,\,von}\par
            \vspace{20mm}
            {\Huge{\@author}}\par
            \vspace{2mm}
            {\LARGE{\@id}} \\ 
            \vspace{2mm}
            {\LARGE{\@email}} \\ 
            \vspace{55mm} 
            \begin{minipage}{0.8\textwidth}
                \centering
                \Large{\@professor\, und \@supervisor} \\ \vspace{2mm}
                {\LARGE\textsc{Forschungsgruppe \\
                Computational Social Science \& Systems Analytics}}
            \end{minipage}
            \end{center}
            \end{minipage}
            \clearpage   
        }
    }{
        \newcommand{\maketitlepage}{
            \begingroup
            \let\clearpage\relax
            \onecolumn
            \thispagestyle{empty}
            \begin{center}
            \includegraphics[width=.3\textwidth]{settings/logos/UniMuenster_Schloss_2023_RGB.png}
        
            \vspace{5mm}
            {\textsc{\Huge Universität Münster}}\par
            \vspace{2mm}
            {\scshape\LARGE Institut für Wirtschaftsinformatik}\par
            \vspace{1cm}
            {\textcolor{gray}{\rule{0.9\textwidth}{0.5mm}}}
            \vspace*{0.5cm}
            \begin{center}
                \begin{minipage}{0.9\textwidth}
                    \begin{center}
                        {\Huge\parindent0pt
                        \begin{spacing}{1.13}
                            \@title
                        \end{spacing}}\par
                    \end{center}
                \end{minipage}
            \end{center}
            \vspace*{-0.3cm}
            {\textcolor{gray}{\rule{0.9\textwidth}{0.5mm}}}\par
            \vspace{20mm}
            \begin{center}
                \begin{minipage}{0.9\textwidth}
                    \begin{center}
                        \Huge \@thesistype
                    \end{center}
                \end{minipage}
            \end{center}
            \vspace{4mm}
            {\Large eingereicht am \@date\,\,von}\par
            \vspace{15mm}
            {\LARGE{\@author}}\par
            \vspace{2mm}
            {{\@id}} \\ 
            \vspace{2mm}
            {{\@email}} \\ 
            \vfill
            \begin{minipage}{0.8\textwidth}
                \centering
                \Large{\@supervisor} \\ \vspace{2mm}
                {\LARGE\textsc{Forschungsgruppe \\
                Computational Social Science \& Systems Analytics}}
            \end{minipage}
            \end{center}
            \clearpage  
            \twocolumn 
            \endgroup
        }
    }
        

    \newcommand{\declaration}{
        \Large 
        \thispagestyle{empty}
        \section*{\LARGE Abschließende Erklärung}
        \vspace{-2mm}
        \noindent \ifcsssa@multiauthor Wir versichern mit der Unterschrift unten, dass wir die Arbeit \textit{\@title} selbständig und ohne fremde Hilfe angefertigt haben und dass wir alle von anderen Autoren wörtlich übernommenen Stellen wie auch die sich an die Gedankengänge anderer Autoren eng anlehnenden Ausführungen unserer Arbeit besonders gekennzeichnet und die Quellen zitiert haben; dies gilt auch für Tabellen, Skizzen, Zeichnungen, bildliche Darstellungen usw.
        \noindent  \else Ich versichere mit der Unterschrift unten, dass ich meine Arbeit \textit{\@title} selbständig und ohne fremde Hilfe angefertigt habe und dass ich alle von anderen Autoren wörtlich übernommenen Stellen wie auch die sich an die Gedankengänge anderer Autoren eng anlehnenden Ausführungen meiner Arbeit besonders gekennzeichnet und die Quellen zitiert habe; dies gilt auch für Tabellen, Skizzen, Zeichnungen, bildliche Darstellungen usw.
        \vspace{-2mm}
    }

    \newcommand{\consent}{
        \Large 
        \section*{\LARGE Einverständniserklärung}
        \vspace{-4mm}
        \textbf{Name:} \@author\\
        \textbf{Titel der Arbeit:} \@title
        
        \noindent  \textbf{Was ist ein Plagiat?} Als ein Plagiat wird eine Übernahme fremden Gedankengutes in die eigene Arbeit angesehen, bei der die Quelle, aus der die Übernahme erfolgt, nicht kenntlich gemacht wird.Es ist dabei unerheblich, ob z.B. fremde Texte wörtlich übernommen werden, nur Strukturen (z.B. argumentative Figuren oder Gliederungen) aus fremden Quellen entlehnt oder Texte aus einer Fremdsprache übersetzt werden.\par
        \noindent  \textbf{Softwarebasierte Überprüfung.} Alle Arbeiten werden vom Prüfungsamt mit Hilfe einer entsprechenden Software auf Plagiate geprüft. Die Arbeit wird zum Zweck der Plagiatsprüfung an einen Software-Dienstleister übermittelt und dort auf Übereinstimmung mit anderen Quellen geprüft. Zum Zweck eines zukünftigen Abgleichs mit anderen Arbeiten wird die Arbeit dauerhaft in einer Datenbank gespeichert. Ein Abruf der Arbeit ist ausschließlich durch die Wirtschaftswissenschaftliche Fakultät der Universität Münster möglich. Studierende erklären sich damit einverstanden, dass allein zum beschriebenen Zweck der Plagiatsprüfung die Arbeit dauerhaft gespeichert und vervielfältigt werden darf. Das Ergebnis der elektronischen Plagiatsprüfung wird dem Erstgutachter mitgeteilt.\par
        \noindent  \textbf{Sanktionen.} Liegt ein Plagiat vor, ist dies ein Täuschungsversuch i.S. der Prüfungsordnung, durch den die Prüfungsleistung als „nicht bestanden“ gewertet wird. Es erfolgt eine Mitteilung an das Prüfungsamt und die dortige Dokumentation. In schwerwiegenden Täuschungsfällen kann der Prüfling von der Prüfung insgesamt ausgeschlossen werden. Dies kann unter Umständen die Exmatrikulation bedeuten. Plagiate können auch nach Abschluss des Prüfungsverfahrens und Verleihung des Hochschulgrades zum Entzug des erworbenen Grades führen. \par
        \noindent  \ifcsssa@multiauthor Hiermit erklären wir, dass wir die obigen Ausführungen gelesen haben und mit dem Verfahren zur Aufdeckung und Sanktionierung von Plagiaten einverstanden sind.
        \noindent  \else Hiermit erkläre ich, dass ich die obigen Ausführungen gelesen habe und mit dem Verfahren zur Aufdeckung und Sanktionierung von Plagiaten einverstanden bin.
        \fi\par
        \noindent  \signatures{Unterschriften}
    }
}{
 \ClassError{csssa}{Unknown language ``\csssa@language'' specified}{}
}}

\newcommand{\thesistype}[1]{\def\@thesistype{#1}}

% Options for types of thesis: bachelor, master, seminar
\ifthenelse{\equal{\csssa@thesis}{seminar}}{
    \ifthenelse{\equal{\csssa@language}{english}}{
        \thesistype{Seminar Thesis in the context of the seminar \textit{\@course} }
    }{
        \thesistype{Abschlussarbeit im Rahmen des Projekt Seminars \textit{\@course} }
    }
}{\ifthenelse{\equal{\csssa@thesis}{master}}{
    \ifthenelse{\equal{\csssa@language}{english}}{
        \thesistype{Master Thesis }
    }{
        \thesistype{Masterarbeit }
    }
}{\ifthenelse{\equal{\csssa@thesis}{bachelor}}{
    \ifthenelse{\equal{\csssa@language}{english}}{
        \thesistype{Bachelor Thesis }
    }{
        \thesistype{Bachelorarbeit }
    }
}{\ClassError{csssa}{Unknown type of thesis ``\csssa@thesis'' specified}{}
}}}


% _______________ Design _______________

% Set indents and line spacing
\setlength{\parindent}{10pt}
\onehalfspacing
\setlength\columnsep{18pt}

% Change footnotes
\RequirePackage[flushmargin,hang,bottom]{footmisc}
\setlength{\footnotemargin}{0.75cm}
\renewcommand\footnoterule{\kern-3pt \hrule width 2in \kern 2.6pt} % Length of separator between text and footnotes
\interfootnotelinepenalty=10000 % Prevent footnotes to be split over multiple pages

% Adjust captions
\captionsetup{figurewithin=none,tablewithin=none} % Continuous numbering
\captionsetup{labelsep=quad} % No separator between label and caption

% Hurenkinder und Schusterjungen verhindern
\clubpenalty=10000
\widowpenalty=10000
\displaywidowpenalty=10000

% Itemization formatting
\setlist[itemize]{label={$-$}, labelindent=16pt,labelsep=18pt,leftmargin=*,topsep=0pt}
\setlist[enumerate,1]{label={\arabic*.},align=left,labelindent=16pt,labelsep=18pt,leftmargin=*,topsep=0pt}

% Format of equation numbering
\renewcommand{\theequation}{\thesection.\arabic{equation}}

% _______________ Commands _______________

% Commands for customizing the title page
\newcommand{\supervisor}[1]{\def\@supervisor{#1}}
\newcommand{\course}[1]{\def\@course{#1}}
\newcommand{\id}[1]{\def\@id{#1}}
\newcommand{\email}[1]{\def\@email{#1}}
\newcommand{\professor}[1]{\def\@professor{#1}}

% Commands for writing the manual
\newcommand{\com}[1]{\texttt{\textbackslash {#1}}}
\newcommand{\combrac}[2]{\texttt{\textbackslash{#1}\{#2\}}}

\newcommand{\englishChairIntro}[1]{\def\@englishChairIntro{#1}}
\newcommand{\germanChairIntro}[1]{\def\@germanChairIntro{#1}}
\newcommand{\englishChair}[1]{\def\@englishChair{#1}}
\newcommand{\germanChair}[1]{\def\@germanChair{#1}}

% Signature for Declarations 
\newcommand{\signatures}[1]{
    \vskip 3em
    \begin{tabular}{@{}p{3in}@{}}
    \hrulefill \\
    \ifcsssa@multiauthor #1
    \else \@author, \@date
    \fi
    \\
  \end{tabular}
}

% _______________ Hard coded information _______________

\englishChair{Computational Social Science \& \\ & Systems Analysis}
\germanChair{Computational Social Science \& \\ & Systems Analysis}
\englishChairIntro{research group}
\germanChairIntro{Forschungsgruppe}


% _______________ Colours _______________

\definecolor{ercis-red}{RGB}{133,35,57}
\definecolor{um-black}{RGB}{62,62,59}
\definecolor{um-green}{RGB}{0,142,150}
\definecolor{um-lightgreen}{RGB}{122,181,22}
\definecolor{um-blue}{RGB}{0,110,137}
\definecolor{um-lightblue}{RGB}{0,157,209}
\definecolor{code-background}{rgb}{0.95, 0.95, 0.96}