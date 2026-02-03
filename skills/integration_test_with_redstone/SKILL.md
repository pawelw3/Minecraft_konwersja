## Proste testy integracyjne z redstone:

Tworzysz strukturę z kablem z niewłączonym redstonem, podłączym do danego BE z GUI akceptującym redstone jako input, tworzysz prosty pipeline z tym BE jako elementem wejściowym który ma dać output na kablu wyjściowym redstone. Na wyjściu tego kabla dajesz commandblock który ma logować jeśli test tej struktury przeszedł.

## Złożone testy integracyjne z modami adapterami:

Architektura testów: 4 warstwy
A) Panel testowy (wejścia)

Źródła sygnału:

dźwignie / przyciski / zegary,

ProjectRed (1.7.10) – timery, sekwencery, logika,

CC / CC:Tweaked – skrypty do sekwencji testów,

Create (1.18.2) – Redstone Link jako „bezprzewodowy patch panel”.

Efekt: masz np. linie sygnałów: TEST_START, PHASE_1, PHASE_2, FAULT_INJECT, RESET.

B) Warstwa adapterów (tłumacz)

To jest serce. Składa się z:

adapterów wejściowych: „jak włączyć/wyłączyć moduł X?”

adapterów wyjściowych: „jak sprawdzić, czy moduł X działa / osiągnął warunek?”

Najważniejsze: adaptery nie muszą sterować wszystkim „wprost”. Często lepiej sterować:

zasilaniem (włącz/wyłącz),

dostępnością wsadu (podaj/odetnij itemy),

odbiorem wyjścia (zablokuj/odetnij output),

routingiem (przełącz ścieżkę),
bo to działa prawie z każdym modem.

C) System pod testem (SUT)

Twoja linia produkcyjna z wielu modów.

D) Asserty i log (wynik testu)

commandblock - wyświetlaj output na konsoli