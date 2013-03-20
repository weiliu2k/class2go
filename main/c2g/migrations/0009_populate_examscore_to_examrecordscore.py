# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        """
        This is a one-time migration to populate the new relation.  It is a bit
        complicated since we don't know exactly which examrecordscore row we
        should point to (which is why this relation is valuable) hence the 
        temporary table and selection logic.

        We special case the celery since we use SQL that's not supported on SQLite.  
        That's safe too do here since we only want reasonable schemas in our 
        celery database, not content like exam scores.
        """
        if db.db_alias == "celery":
            return

        if not db.dry_run:
            
            #This migration back populates the c2g_examscore.examrecordscore_id foreign key.
            #Initially I did this in Django code but the performance was poor so this is much faster but
            #more in the realms of SQL.
            
            #This command creates a temp table to be used later
            print "This migration back populates the new c2g_examscore.examrecordscore_id relation; it may take a few minutes."
            print "Creating temp table examscore_pop_new_relation"
            db.execute('CREATE TABLE `examscore_pop_new_relation` \
                      (`student_id` int(11) NOT NULL, \
                       `exam_id` int(11) NOT NULL, \
                       `es_score` double default NULL, \
                       `er_score` double default NULL, \
                       `er_id` int(11) default NULL, \
                       `es_id` int(11) NOT NULL default \'0\', \
                       `ers_id` int(11) default NULL, \
                       UNIQUE KEY `es_ers_id` (`es_id`) ) ENGINE=MyISAM')
        
        
            #Need to chuck up the inserts into the temp table and do in a transaction as otherwise I run into
            #exceeding available table locks error.
            print "Populating the temp table"
            start = 0
            while start < 200000:
                start_val = str(start)
                end_val = str(start + 500)
         
                db.start_transaction()
                db.execute("insert into examscore_pop_new_relation \
                          (select er.student_id, \
                           er.exam_id, \
                           es.score \"es_score\", \
                           er.score \"er.score\", \
                           max(er.id) \"er_id\", \
                           es.id \"es_id\", \
                           max(ers.id) \"ers_id\" \
                           from c2g_examrecord er, c2g_examscore es, c2g_examrecordscore ers \
                           where er.student_id = es.student_id \
                           and er.exam_id = es.exam_id \
                           and er.score = es.score \
                           and er.complete = 1 \
                           and ers.record_id = er.id \
                           and er.student_id > " + start_val + "\
                           and er.student_id <= " + end_val + "\
                           group by er.student_id, er.exam_id)")
            
                start += 500
                db.commit_transaction()
            
            print "Updating c2g_examscore records"
            db.execute('update c2g_examscore es, examscore_pop_new_relation espnr \
                        set es.examrecordscore_id = espnr.ers_id \
                        where es.id = espnr.es_id')
            
            print "Deleting the temp table"
            db.execute('drop table examscore_pop_new_relation')
            
            print "All done."

    def backwards(self, orm):
        pass

    models = {
        'auth.group': {
            'Meta': {'object_name': 'Group'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        'auth.permission': {
            'Meta': {'ordering': "('content_type__app_label', 'content_type__model', 'codename')", 'unique_together': "(('content_type', 'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['contenttypes.ContentType']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        'c2g.additionalpage': {
            'Meta': {'object_name': 'AdditionalPage', 'db_table': "u'c2g_additional_pages'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['c2g.AdditionalPage']"}),
            'index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'live_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'menu_slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'mode': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.ContentSection']", 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'c2g.announcement': {
            'Meta': {'object_name': 'Announcement', 'db_table': "u'c2g_announcements'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['c2g.Announcement']"}),
            'index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'live_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'mode': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'owner': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'c2g.contentgroup': {
            'Meta': {'object_name': 'ContentGroup', 'db_table': "u'c2g_content_group'"},
            'additional_page': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.AdditionalPage']", 'null': 'True', 'blank': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'display_style': ('django.db.models.fields.CharField', [], {'default': "'list'", 'max_length': '32', 'blank': 'True'}),
            'exam': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Exam']", 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.File']", 'null': 'True', 'blank': 'True'}),
            'group_id': ('django.db.models.fields.IntegerField', [], {'db_index': 'True', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'level': ('django.db.models.fields.IntegerField', [], {'db_index': 'True'}),
            'problemSet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.ProblemSet']", 'null': 'True', 'blank': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Video']", 'null': 'True', 'blank': 'True'})
        },
        'c2g.contentsection': {
            'Meta': {'object_name': 'ContentSection', 'db_table': "u'c2g_content_sections'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['c2g.ContentSection']"}),
            'index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'live_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'mode': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'subtitle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'c2g.course': {
            'Meta': {'object_name': 'Course', 'db_table': "u'c2g_courses'"},
            'accompanying_materials': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'calendar_end': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'calendar_start': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'contact': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'faq': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'handle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['c2g.Course']"}),
            'institution': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Institution']", 'null': 'True'}),
            'institution_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'instructor_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'instructor_group'", 'to': "orm['auth.Group']"}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'list_publicly': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'live_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'logo': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'mode': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'outcomes': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'piazza_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'preenroll_only': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'prerequisites': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'preview_only_mode': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'readonly_tas_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'readonly_tas_group'", 'to': "orm['auth.Group']"}),
            'share_to': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'share_from'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['c2g.Course']"}),
            'short_description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'student_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'student_group'", 'to': "orm['auth.Group']"}),
            'syllabus': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'tas_group': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'tas_group'", 'to': "orm['auth.Group']"}),
            'term': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'twitter_tag': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'year': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        'c2g.coursecertificate': {
            'Meta': {'object_name': 'CourseCertificate'},
            'assets': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'storage': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'completion'", 'max_length': '64'})
        },
        'c2g.courseemail': {
            'Meta': {'object_name': 'CourseEmail', 'db_table': "u'c2g_course_emails'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'html_message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'to': ('django.db.models.fields.CharField', [], {'default': "'myself'", 'max_length': '64'})
        },
        'c2g.courseinstructor': {
            'Meta': {'object_name': 'CourseInstructor', 'db_table': "u'c2g_course_instructor'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'instructor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Instructor']"}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'c2g.coursestudentlist': {
            'Meta': {'object_name': 'CourseStudentList'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'max_completion_level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'c2g.currenttermmap': {
            'Meta': {'object_name': 'CurrentTermMap'},
            'course_prefix': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '64', 'db_index': 'True'}),
            'course_suffix': ('django.db.models.fields.CharField', [], {'max_length': '64'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'c2g.emailaddr': {
            'Meta': {'object_name': 'EmailAddr'},
            'addr': ('django.db.models.fields.EmailField', [], {'max_length': '128'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'optout': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'optout_code': ('django.db.models.fields.CharField', [], {'default': "'optout'", 'max_length': '64'})
        },
        'c2g.exam': {
            'Meta': {'object_name': 'Exam'},
            'assessment_type': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True', 'blank': 'True'}),
            'autograde': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'display_single': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'due_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'exam_type': ('django.db.models.fields.CharField', [], {'default': "'exam'", 'max_length': '32'}),
            'grace_period': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'grade_single': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'html_content': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['c2g.Exam']"}),
            'index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'invideo': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'late_penalty': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'live_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'minutes_btw_attempts': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'minutesallowed': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'mode': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'partial_credit_deadline': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'quizdown': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'resubmission_penalty': ('django.db.models.fields.IntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.ContentSection']", 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'null': 'True'}),
            'submissions_permitted': ('django.db.models.fields.IntegerField', [], {'default': '999', 'null': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'timed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'total_score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'xml_imported': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'xml_metadata': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'c2g.examrecord': {
            'Meta': {'object_name': 'ExamRecord'},
            'attempt_number': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'complete': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'exam': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Exam']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'json_data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'json_score_data': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'late': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'onpage': ('django.db.models.fields.CharField', [], {'max_length': '512', 'null': 'True', 'blank': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'c2g.examrecordfieldlog': {
            'Meta': {'object_name': 'ExamRecordFieldLog'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'exam': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Exam']"}),
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'human_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'max_score': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'raw_score': ('django.db.models.fields.FloatField', [], {'default': '0', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'c2g.examrecordscore': {
            'Meta': {'object_name': 'ExamRecordScore'},
            'csv_imported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'raw_score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'record': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['c2g.ExamRecord']", 'unique': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'c2g.examrecordscorefield': {
            'Meta': {'object_name': 'ExamRecordScoreField'},
            'associated_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'correct': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'human_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.ExamRecordScore']"}),
            'subscore': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'})
        },
        'c2g.examrecordscorefieldchoice': {
            'Meta': {'object_name': 'ExamRecordScoreFieldChoice'},
            'associated_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'choice_value': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'correct': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'human_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.ExamRecordScoreField']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'c2g.examscore': {
            'Meta': {'unique_together': "(('exam', 'student'),)", 'object_name': 'ExamScore'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'csv_imported': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'exam': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Exam']"}),
            'examrecordscore': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.ExamRecordScore']", 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'score': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'c2g.examscorefield': {
            'Meta': {'object_name': 'ExamScoreField'},
            'associated_text': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'correct': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'}),
            'field_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'human_name': ('django.db.models.fields.CharField', [], {'db_index': 'True', 'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.ExamScore']"}),
            'subscore': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'})
        },
        'c2g.exercise': {
            'Meta': {'object_name': 'Exercise', 'db_table': "u'c2g_exercises'"},
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'null': 'True'}),
            'fileName': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'handle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'problemSet': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['c2g.ProblemSet']", 'through': "orm['c2g.ProblemSetToExercise']", 'symmetrical': 'False'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'video': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['c2g.Video']", 'through': "orm['c2g.VideoToExercise']", 'symmetrical': 'False'})
        },
        'c2g.file': {
            'Meta': {'object_name': 'File', 'db_table': "u'c2g_files'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'handle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['c2g.File']"}),
            'index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'live_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'mode': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.ContentSection']", 'null': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'c2g.institution': {
            'Meta': {'object_name': 'Institution', 'db_table': "u'c2g_institutions'"},
            'city': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'country': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'domains': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.TextField', [], {})
        },
        'c2g.instructor': {
            'Meta': {'object_name': 'Instructor'},
            'biography': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'email': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'handle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'photo': ('django.db.models.fields.files.FileField', [], {'max_length': '100', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'c2g.listemail': {
            'Meta': {'object_name': 'ListEmail'},
            'from_addr': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'from_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'hash': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'html_message': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'sender': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': "orm['auth.User']", 'null': 'True', 'blank': 'True'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'to_list': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.MailingList']"})
        },
        'c2g.mailinglist': {
            'Meta': {'object_name': 'MailingList'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['c2g.EmailAddr']", 'symmetrical': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'})
        },
        'c2g.newsevent': {
            'Meta': {'object_name': 'NewsEvent', 'db_table': "u'c2g_news_events'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'event': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'c2g.pagevisitlog': {
            'Meta': {'object_name': 'PageVisitLog', 'db_table': "u'c2g_page_visit_log'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'object_id': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'page_type': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"})
        },
        'c2g.problemactivity': {
            'Meta': {'object_name': 'ProblemActivity', 'db_table': "u'c2g_problem_activity'"},
            'attempt_content': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'attempt_number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'card': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'cards_done': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'cards_left': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'casing': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'complete': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'count_hints': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'problem_identifier': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'problem_type': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'problemset_to_exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.ProblemSetToExercise']", 'null': 'True'}),
            'review_mode': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'seed': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sha1': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'time_taken': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'topic_mode': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'user_choices': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'user_selection_val': ('django.db.models.fields.CharField', [], {'max_length': '1024', 'null': 'True', 'blank': 'True'}),
            'video_to_exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.VideoToExercise']", 'null': 'True'})
        },
        'c2g.problemset': {
            'Meta': {'object_name': 'ProblemSet', 'db_table': "u'c2g_problem_sets'"},
            'assessment_type': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'due_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True'}),
            'grace_period': ('django.db.models.fields.DateTimeField', [], {}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['c2g.ProblemSet']"}),
            'index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'late_penalty': ('django.db.models.fields.IntegerField', [], {}),
            'live_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'mode': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'partial_credit_deadline': ('django.db.models.fields.DateTimeField', [], {}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'randomize': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'resubmission_penalty': ('django.db.models.fields.IntegerField', [], {}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.ContentSection']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50'}),
            'submissions_permitted': ('django.db.models.fields.IntegerField', [], {}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'c2g.problemsettoexercise': {
            'Meta': {'object_name': 'ProblemSetToExercise', 'db_table': "u'c2g_problemset_to_exercise'"},
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Exercise']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.ProblemSetToExercise']", 'null': 'True', 'blank': 'True'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'mode': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'number': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'problemSet': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.ProblemSet']"})
        },
        'c2g.studentexamstart': {
            'Meta': {'object_name': 'StudentExamStart'},
            'exam': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Exam']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'c2g.studentinvitation': {
            'Meta': {'object_name': 'StudentInvitation'},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '128', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'})
        },
        'c2g.studentsection': {
            'Meta': {'object_name': 'StudentSection', 'db_table': "u'c2g_sections'"},
            'capacity': ('django.db.models.fields.IntegerField', [], {'default': '999'}),
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'members': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['auth.User']", 'symmetrical': 'False'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'c2g.userprofile': {
            'Meta': {'object_name': 'UserProfile', 'db_table': "u'c2g_user_profiles'"},
            'accept_language': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'accept_language_first': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'birth_year': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'certificates': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['c2g.CourseCertificate']", 'symmetrical': 'False'}),
            'client_ip': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'client_ip_first': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True'}),
            'education': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'email_me': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '64', 'null': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'institutions': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['c2g.Institution']", 'symmetrical': 'False'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'piazza_email': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'piazza_name': ('django.db.models.fields.CharField', [], {'max_length': '128', 'blank': 'True'}),
            'referrer': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'referrer_first': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'site_data': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['auth.User']", 'unique': 'True'}),
            'user_agent': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'user_agent_first': ('django.db.models.fields.CharField', [], {'max_length': '256', 'null': 'True'}),
            'work': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True'})
        },
        'c2g.video': {
            'Meta': {'object_name': 'Video', 'db_table': "u'c2g_videos'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'duration': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'exam': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Exam']", 'null': 'True', 'blank': 'True'}),
            'file': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'handle': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'db_index': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': "orm['c2g.Video']"}),
            'index': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'live_datetime': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'mode': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'section': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.ContentSection']", 'null': 'True'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '255', 'null': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'youtube'", 'max_length': '30'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'})
        },
        'c2g.videoactivity': {
            'Meta': {'object_name': 'VideoActivity', 'db_table': "u'c2g_video_activity'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'max_end_seconds': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'start_seconds': ('django.db.models.fields.IntegerField', [], {'default': '0', 'blank': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Video']"})
        },
        'c2g.videodownload': {
            'Meta': {'object_name': 'VideoDownload', 'db_table': "u'c2g_video_download'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'download_date': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'format': ('django.db.models.fields.CharField', [], {'max_length': '35', 'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'student': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Video']"})
        },
        'c2g.videotoexercise': {
            'Meta': {'object_name': 'VideoToExercise', 'db_table': "u'c2g_video_to_exercise'"},
            'exercise': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Exercise']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.VideoToExercise']", 'null': 'True', 'blank': 'True'}),
            'is_deleted': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'mode': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Video']"}),
            'video_time': ('django.db.models.fields.IntegerField', [], {})
        },
        'c2g.videoviewtraces': {
            'Meta': {'object_name': 'VideoViewTraces', 'db_table': "u'c2g_video_view_traces'"},
            'course': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Course']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'time_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'trace': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['auth.User']"}),
            'video': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['c2g.Video']"})
        },
        'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['c2g']
