.. _calendar:

========
Calendar
========

Modern HTML nowadays offers input fields with built-in date and date-time pickers. Usually there
is no need to use a special widget accepting datestamps. However, the built-in date and date-time
pickers are impossible to style using CSS or other means. It therefore is impossible to attach
context information to the dates and times.

The JavaScript ecosystem offers a huge set of libraries with alternative date- and time-pickers,
for instance Flatpickr_ or Pikaday_ to name a few with no external dependencies. Using one of those
would of course be an option. However, it then still is not possible to change the rendering context
based on information only available on the server, for instance the vacancy of reservable time
slots.

.. _Flatpickr: https://flatpickr.js.org/
.. _Pikaday: https://github.com/Pikaday/Pikaday

JavaScript does not offer any functionality for non-trivial date arithmetic, so this has to be
implemented by every date picker. On the other hand, in **django-formset** the calendar widget is
rendered by the server, using Python's built-in Calendar_ class. This allows us to use the Django
template language to style the layout of the rendered calendar and add context on information only
available to the server.


.. _date-picker:

Date Picker Widget
==================

In our form, we want to add a field to enter the publishing date of our blog. By using
:class:`formset.widgets.DatePicker` instead of the default widget, this input field opens a
calendar, whenever the user clicks on it. This calendar differs from the default HTML date picker,
which is rendered when using the widget :class:`formset.widgets.DateInput`. While technically
possible, it is not recommended to interchange them on the same page or even application as this
results in unexpected user experience.

.. django-view:: blog_form
	:hide-view:
	:caption: form.py

	from django.forms import fields, forms
	from formset.widgets import DatePicker, DateTimePicker
	
	class BlogForm(forms.Form):
	    publish_date = fields.DateField(widget=DatePicker)

	    # other fields

When paginating through calendar sheets, each sheet must be fetched from the server. Therefore the
view controlling our blog form must inherit from the special mixin class
:class:`formset.calendar.CalendarResponseMixin`. This class listens on the supplied endpoint and
responds with a HTML snippet of the next sheet.

.. django-view:: blog_view
	:view-function: BlogView.as_view(extra_context={'framework': 'bootstrap', 'pre_id': 'blog-result'}, form_kwargs={'auto_id': 'bl_id_%s'})
	:caption: view.py

	from formset.calendar import CalendarResponseMixin
	from formset.views import FormView

	class BlogView(CalendarResponseMixin, FormView):
	    form_class = BlogForm
	    template_name = "form.html"
	    success_url = "/success"

The date format used by the input field adopts itself to the browser's current locale setting. This
means that in the Anglo Saxon area, dates are formatted as ``mm/dd/yyyy``, whereas in Europe they are
formatted as ``dd.mm.yyyy``. Japan uses ``yyyy/mm/dd`` as date format. This setting can be
overridden by adding the attribute ``date-format`` to the widget during instantiation, for instance
``DatePicker(attrs={"date-format": "iso"})``.


Date-Time Picker Widget
=======================

In our form, we want to add a field to enter the launch date and time. By using
:class:`formset.widgets.DateTimePicker` instead of the default widget, this input field opens a
calendar, whenever the user clicks on it. This calendar differs from the default HTML date picker,
which is rendered when using the widget :class:`formset.widgets.DateTimeInput`. While technically
possible, it is not recomended to interchange them on the same page or even application as this
results in unexpected user experience.

By clicking on a date inside the ``DateTimePicker`` widget, a 24h view appears. Depending on the
chosen value for the ``step`` attribute , the user can then select a certain time interval. The
``step`` attribute must be of Python type ``datetime.timedelta`` and can have one of these values:
``timedelta(minutes=5)``, ``timedelta(minutes=10)``, ``timedelta(minutes=15)``,
``timedelta(minutes=20)``, ``timedelta(minutes=30)``, ``timedelta(hours=1)``,
``timedelta(hours=2)``, ``timedelta(hours=3)``, ``timedelta(hours=4)``, ``timedelta(hours=6)``,
``timedelta(hours=8)`` and ``timedelta(hours=12)``. This defines the granularity of the timestamp
the user can select.

.. django-view:: launch_form
	:caption: form.py

	from datetime import timedelta
	
	class LaunchForm(forms.Form):
	    start_datetime = fields.DateTimeField(
	        widget=DateTimePicker(attrs={'step': timedelta(minutes=5)})
	    )


.. django-view:: launch_view
	:view-function: LaunchView.as_view(extra_context={'framework': 'bootstrap', 'pre_id': 'launch-result'}, form_kwargs={'auto_id': 'lf_id_%s'})
	:hide-code:

	class LaunchView(CalendarResponseMixin, FormView):
	    form_class = LaunchForm
	    template_name = "form.html"
	    success_url = "/success"


Date and Time Constraints
=========================

Both widgets :class:`formset.widgets.DatePicker` and :class:`formset.widgets.DateTimePicker` respect
the minimum and maximum values passed to the widget ``DatePicker`` and ``DateTimePicker``. By
combining it with ``now`` and ``timedelta`` this becomes very useful, since it prevents users from
selecting dates too far in the past or in the future.

.. django-view:: appointment_form
	:caption: form.py

	from django.utils.timezone import now
	
	class AppointmentForm(forms.Form):
	    date = fields.DateField(
	        widget=DatePicker(attrs={
	            'min': now().isoformat(),
	            'max': (now() + timedelta(weeks=2)).isoformat(),
	        }),
	    )

This example disables all dates which lie in the past and are more than two weeks in the future.

.. django-view:: appointment_view
	:view-function: AppointmentView.as_view(extra_context={'framework': 'bootstrap', 'pre_id': 'appointment-result'}, form_kwargs={'auto_id': 'af_id_%s'})
	:hide-code:

	class AppointmentView(CalendarResponseMixin, FormView):
	    form_class = AppointmentForm
	    template_name = "form.html"
	    success_url = "/success"


Applying Context to a Picker
============================

Apart from not having to integrate date arithmetics into the client-side part of this library, one
of the big advantages of using a server side rendered calendar sheet is, that we are able to enrich
the rendering context with additional data. Say that we want to show the phases of the moon for each
date (this of course could also be done in JavaScript, but here it is used for simple demonstration
purposes). Normally one would use some information stored in the database, for instance to display
vacant or occupied rooms in a booking application. Or it can be useful to display extra information
such as holidays.

.. django-view:: moon_form
	:caption: form.py

	from datetime import datetime
	from decimal import Decimal
	from math import floor
	from formset.calendar import CalendarRenderer, ViewMode

	class MoonCalendarRenderer(CalendarRenderer):
	    # Calculate lunar phase by Sean B. Palmer, inamidst.com
	    # http://en.wikipedia.org/wiki/Lunar_phase#Lunar_phase_calculation
	    phases = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
	
	    def position(self, then):
	        diff = then - datetime(2001, 1, 1)
	        days = Decimal(diff.days) + Decimal(diff.seconds) / Decimal(86400)
	        lunations = Decimal('0.20439731') + days * Decimal('0.03386319269')
	        return lunations % Decimal(1)
	
	    def phase(self, pos):
	        index = pos * Decimal(8) + Decimal('0.5')
	        index = int(floor(index)) & 7
	        return self.phases[index]
	
	    def get_template_name(self, view_mode):
	        if view_mode == ViewMode.weeks:
	            return 'calendar/weeks-moon.html'
	        return super().get_template_name(view_mode)
	
	    def get_context_weeks(self):
	        context = super().get_context_weeks()
	        monthdays = []
	        for monthday in context['monthdays']:
	            phase = self.phase(self.position(datetime.fromisoformat(monthday[0])))
	            monthdays.append((*monthday, phase))
	        context['monthdays'] = monthdays
	        return context

	class MoonForm(forms.Form):
	    date = fields.DateField(
	        label="Some Date",
	        widget=DatePicker(calendar_renderer=MoonCalendarRenderer),
	    )

Since this view requires a modified renderer to add additional context, we must tell our special
mixin class :class:`formset.calendar.CalendarResponseMixin` to use that by passing it as
``calendar_renderer_class``.

.. django-view:: moon_view
	:view-function: MoonView.as_view(extra_context={'framework': 'bootstrap', 'pre_id': 'moon-result'}, form_kwargs={'auto_id': 'mf_id_%s'})
	:caption: view.py
	:emphasize-lines: 3

	class MoonView(CalendarResponseMixin, FormView):
	    form_class = MoonForm
	    calendar_renderer_class = MoonCalendarRenderer
	    template_name = "form.html"
	    success_url = "/success"
