# Copyright 2008 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from django.conf.urls.defaults import *



urlpatterns = patterns(
	'',
	(r'^$', 'home.index'),
	(r'^join$', 'join.go'),
	(r'^leave$', 'leave.go'),
	(r'^player/(\d+)$', 'viewplayer.go'),
	(r'^setup$', 'main.setup'),
	(r'^test$', 'test.test'),
	(r'^testcron$', 'testcron.testcron'),
	(r'^cron$', 'cron.go'),
	(r'^players_are_gated$','players_are_gated.go'),
	(r'^cannot_join$','players_are_gated.cannot_join'),
	(r'^tourneys$', 'home.display_tourneys'),


	(r'^tourneys/(\d+)/join$', 'join.go'),
	(r'^tourneys/(\d+)$', 'home.index_new'),
	(r'^tourneys/(\d+)/player/(\d+)$', 'viewplayer.go'),
	
	(r'^myadmin_players$', 'admin.myadmin_players'),
	(r'^myadmin_tourneys$', 'admin.myadmin_tourneys'),
	
	(r'^tourneys/(\d+)/testcron$', 'testcron.testcron_one_tourney'),
	
	)

