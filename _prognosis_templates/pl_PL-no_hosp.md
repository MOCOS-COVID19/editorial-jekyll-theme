---
layout: document
lang: pl
category: prognoza
date: %datedotreversed%
sortable_date: %date%
title: Krótkoterminowa prognoza rozwoju pandemii po %datedotreversed% 
teaser: Prezentujemy wyniki krótkoterminowego modelowania rozwoju pandemii po %datedotreversed%.
description: Prezentujemy wyniki krótkoterminowego modelowania rozwoju pandemii po %datedotreversed%.
html_chart: /assets/images/reports/%date%/prognoza_pl.html
html_chart_d: /assets/images/reports/%date%/prognoza_pl_deaths.html
image_teaser:  /assets/images/reports/%date%/prognoza_pl.png
image:  /assets/images/reports/%date%/prognoza_pl.png
---

Prezentujemy wyniki krótkoterminowego modelowania rozwoju pandemii.

<div style="text-align: center" class="row 80%">
    <span class="image fit">
        <iframe src="{{ page.html_chart }}" alt="" style="width: 100%; height:54em;"></iframe>
    </span>
</div>

<div style="text-align: center" class="row 80%">
    <span class="image fit">
        <iframe src="{{ page.html_chart_d }}" alt="" style="width: 100%; height:54em;"></iframe>
    </span>
</div>
