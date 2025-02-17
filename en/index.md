---
layout: default
lang: en
title: Main Page
---

{% assign forecasts = site.prognosis_en | reverse %}

{% for forecast in forecasts limit: 1 %}

<section id="banner">
    <div class="content">
      <header>
        <h1>{{ forecast.title }} </h1>
        <p>current forecast</p>
      </header>
      <p>{{ forecast.teaser }}</p>
      <ul class="actions">
        <li><a href="{{ forecast | absolute_url }}" class="button big">Więcej</a></li>
      </ul>
    </div>
    <span class="image object">
      {% if forecast.html_chart %}
      <iframe src="{{ forecast.html_chart }}" alt="" style="width: 100%; height:100%;"></iframe>
      {% else %}
      <img src="{{ forecast.image_teaser }}" alt="" />
      {% endif %}
    </span>
  </section>

{% endfor %}

<!-- Section -->
<section>
	<header class="major">
		<h2>There's more to our work than just forecasting:</h2>
	</header>
	<div class="features">
		<article>
			<span class="icon fa-calculator"></span>
			<div class="content">
				<h3><a href="/en/risk.html">COVID-19 Individual Risk Assessment</a></h3>
				<p>Are you interested in estimating the individual probability of conditional death or hospitalization? 
                MOCOS members have built a risk model based on data from the first half of the year.</p>
			</div>
		</article>
		<article>
			<span class="icon fa-line-chart"></span>
			<div class="content">
				<h3><a href="/en/automatic.html">COVID-19 German & Polish Forecast HUB</a></h3>
				<p>The MOCOS model is part of the German & Polish COVID-19 Forecast HUB. You will find there forecasts of the development of the epidemic for the next 2 weeks for Poland.</p>

			</div>
		</article>
	</div>
</section>

<!-- Section -->
<!-- section>
	<header class="major">
		<h2>Analyses</h2>
	</header -->

{% assign analyses = site.analysis_en | reverse %}
<div class="posts">
{% for analysis in analyses %}	
		<article>
			<a href="{{ analysis | absolute_url }}" class="image"><img src="{{ analysis.image_teaser }}" alt="" /></a>
			<h3>{{ analysis.title }}</h3>
			<p>{{ analysis.teaser }}</p>
			<ul class="actions">
				<li><a href="{{ analysis | absolute_url }}" class="button">More</a></li>
			</ul>
		</article>
{% endfor %}
</div>
