import datetime
import random
import re

from flask import request, render_template, redirect
from flask.ext.login import current_user, login_user, logout_user, login_required
from crowd import crowd
from serveus.forms import LoginForm, RecoveryForm
# IMPORT MODELS HERE
from serveus.models import User
from crowd.models import db, Labeler, LabelerType, TrainingImage, TrainingImageLabel, TrainingImageLabelCell

# global values
top_n_labels = 5
label_limit = 3
approval_percent = 0.51

@crowd.route('/crowd/')
@crowd.route('/crowd/index/')
def index():
    if current_user.is_authenticated():
        return redirect('/crowd/dashboard/')
    return render_template("/crowd/index.html", login_form = LoginForm())
    
@crowd.route('/crowd/dashboard/')
@login_required
def dashboard():
    totalUnlabeled = TrainingImage.query.filter_by(date_finalized = None).count()
    totalLabeled = len(TrainingImage.query.all()) - totalUnlabeled
    expertNeeded = TrainingImage.query.filter_by(final_label_1 = 'Undeterminable').count()
    leaderboard = Labeler.query.order_by(Labeler.labeler_rating).limit(10)
    # sort leaderboard so Cat is not last:))
    labeler = Labeler.query.filter_by(user_id=current_user.id).first()
    total_images_labeled = TrainingImageLabel.query.group_by(TrainingImageLabel.training_image_id).count()
    
   
    
    return render_template("/crowd/dashboard.html", user = current_user, labeler = labeler, totalUnlabeled = totalUnlabeled, totalLabeled = totalLabeled, expertNeeded = expertNeeded, leaderboard = leaderboard, total_images_labeled=total_images_labeled)

def makeTrainingImageLabel(labeler, diagnosis, coordinates):
    global label_limit
    label = TrainingImageLabel(labeler.id, labeler.current_training_image_id, datetime.datetime.now().date(), labeler.last_session.time(), datetime.datetime.now().time(), diagnosis, None, None)
    db.session.add(label)
    db.session.commit()
    if coordinates != None:
        cell_list = [TrainingImageLabelCell(label.id, x, y, None, None) for x,y in coordinates]
        for i in cell_list:
            db.session.add(i)
        db.session.commit()
    
    current_training_image = label.trainingimage
    
    
    total_unique_labelers = TrainingImageLabel.query.filter_by(training_image_id = current_training_image.id).group_by(TrainingImageLabel.labeler_id).count()
    
    print 'ASDASJDLKASHJDLAKSFHKAJSFHKAJFHLSAHDLKASDJ'
    print str(total_unique_labelers)
    
    if total_unique_labelers >= label_limit:
        return 'Not accepting anymore labels for this image'
        
    if total_unique_labelers < label_limit:
        current_training_image.total_labels += 1
    
    print 'LABELER TYPE'
    print labeler.labelertype
    
    # limit reached
    if total_unique_labelers >= label_limit or str(labeler.labelertype) == 'Expert':
        print 'EXPERT SIYA'
        label_list = {'No Malaria':[], 'Falciparum':[], 'Vivax':[], 'Malariae':[], 'Ovale':[]}
        label_total = 0
        percent_list = {'No Malaria':0, 'Falciparum':0, 'Vivax':0, 'Malariae':0, 'Ovale':0}
        for i in current_training_image.training_image_labels[0:]:
            label_list[i.initial_label].append(i)
            label_total += 1
            
        # 1cho's sorting algo, not working
        '''
        sorted_list = sorted(map(lambda x: (x, len(x), x[0].initial_label), filter(label_list.values(), lambda x: len(x) != 0)))[:2]
        '''
        
        # Calculate label weights with respect to labeler rating
        total_label_weight = 0.0
        label_weight = {'No Malaria':0.0, 'Falciparum':0.0, 'Vivax':0.0, 'Malariae':0.0, 'Ovale':0.0}

        for i in label_list:
            for j in label_list[i]:
                label_weight[i] += j.labeler.labeler_rating
                total_label_weight += j.labeler.labeler_rating

        # print label_weight

        # Calculate percents with respect to weights
        label_percent = {'No Malaria':0.0, 'Falciparum':0.0, 'Vivax':0.0, 'Malariae':0.0, 'Ovale':0.0}
        for i in label_weight:
            label_percent[i] = label_weight[i]/total_label_weight

        # print label_percent
    
        global approval_percent
        # Get majority label >= approval_percent
        final_label = 'Undeterminable'
        for i in label_percent:
            if label_percent[i] >= approval_percent:
                final_label = i
                break

        # print final_label

        # IF LABELER IS AN EXPERT
        if labeler.labelertype == 'Expert':
            final_label = label.initial_diagnosis

        # Finalize label
        current_training_image.final_label_1 = final_label
        current_training_image.date_finalized = datetime.datetime.now()
        db.session.add(current_training_image)

        for i in label_list:
            for j in label_list[i]:
                j.correct_label = final_label
                j.labeler.total_images_labeled += 1
                if j.initial_label == final_label:
                    j.labeler_correct = True
                    j.labeler.total_correct_images_labeled += 1
                    # INCREASE LABELER RATING
                else:
                    # DECREASE LABELER RATING
                    pass
                db.session.add(j)
                db.session.add(j.labeler)

        db.session.commit()
        
@crowd.route('/crowd/gallery/')
@login_required
def gallery():
    totalUnlabeled = TrainingImage.query.filter_by(date_finalized = None).count()
    totalLabeled = len(TrainingImage.query.all()) - totalUnlabeled
    expertNeeded = TrainingImage.query.filter_by(final_label_1 = 'Undeterminable').count()
    leaderboard = Labeler.query.order_by(Labeler.labeler_rating).limit(10)
    # sort leaderboard so Cat is not last:))
    labeler = Labeler.query.filter_by(user_id=current_user.id).first()
    total_images_labeled = TrainingImageLabel.query.group_by(TrainingImageLabel.training_image_id).count()
    
    return render_template("/crowd/gallery.html", user = current_user, labeler = labeler, totalUnlabeled = totalUnlabeled, totalLabeled = totalLabeled, expertNeeded = expertNeeded, leaderboard = leaderboard, total_images_labeled=total_images_labeled)

@crowd.route('/crowd/quiz/',  methods = ['GET', 'POST'])
@login_required
def quiz():
    if request.method == 'GET' : 
        labeler = Labeler.query.filter_by(user_id=current_user.id).first()
   # random.shuffle(quizlist) #to be removed later
        quizlist = [ids.id for ids in TrainingImage.query.all()]
            
        quizlen = len(quizlist)
        quizind = [0 for i in range(quizlen)]
        counter=0
        for i in quizlist:
            quizind[counter]=counter
            counter+=1
        #array of index
        random.shuffle(quizlist)
        print quizlist
        #sample training image
        training_image_to_label=TrainingImage.query.get(quizlist[0])
        
        return render_template("/crowd/quiz.html", user = current_user, labeler = labeler,  training_image_to_label=training_image_to_label, quizind = quizind, quizlist=quizlist)
        
    elif request.method == 'POST':
       temp = request.form["ind"]
       print TrainingImage.query.get(temp).image_id
       temp2 = TrainingImage.query.get(temp).image_id
      #  print TrainingImage.query.get(temp)
      #  return training_image_to_label
       return 'pic/' + str(temp2)

    
@crowd.route('/crowd/session/',  methods = ['GET', 'POST'])
@login_required
def session():
    # Constants
    labeler = Labeler.query.filter_by(user_id=current_user.id).first()
    template = "/crowd/session.html"
    
    # LABEL SUBMITTED
    if request.method == 'POST' and request.form:
        # Check if data submitted in request.form is valid
        
        # Print all for debugging
        for i in request.form:
            print i + ': ' + request.form[i]
        
        # Unsure
        if request.form.getlist('unsure'):
            makeTrainingImageLabel(labeler, 'Undeterminable', None)
            
        else:
            # No Malaria
            #if not request.form.getlist('with_malaria'):
            if not (request.form.getlist('with_falciparum') or request.form.getlist('with_vivax') or request.form.getlist('with_malariae') or request.form.getlist('with_ovale')):
                makeTrainingImageLabel(labeler, 'No Malaria', None)
                
            else:
                # With Falciparum
                if request.form.getlist('with_falciparum'):
                    # String to tuples
                    coordinates = [(tuple(int(j) for j in re.split(',',i))) for i in re.findall('[0-9]+,[0-9]+', str(request.form.getlist('falciparum_coordinates')))]
                    makeTrainingImageLabel(labeler, 'Falciparum', coordinates)
                
                # With Vivax
                if request.form.getlist('with_vivax'):
                    coordinates = [(tuple(int(j) for j in re.split(',',i))) for i in re.findall('[0-9]+,[0-9]+', str(request.form.getlist('vivax_coordinates')))]
                    makeTrainingImageLabel(labeler, 'Vivax', coordinates)
                    
                # With Malariae
                if request.form.getlist('with_malariae'):
                    coordinates = [(tuple(int(j) for j in re.split(',',i))) for i in re.findall('[0-9]+,[0-9]+', str(request.form.getlist('malariae_coordinates')))]
                    makeTrainingImageLabel(labeler, 'Malariae', coordinates)
                    
                # With Ovale
                if request.form.getlist('with_ovale'):
                    coordinates = [(tuple(int(j) for j in re.split(',',i))) for i in re.findall('[0-9]+,[0-9]+', str(request.form.getlist('ovale_coordinates')))]
                    makeTrainingImageLabel(labeler, 'Ovale', coordinates)
            
        # DONE LABELING
        # UNCOMMENT NEXT LINES TO REMOVE PENDING LABEL FROM LABELER
        labeler.current_training_image_id = None
        labeler.last_session = datetime.datetime.now()
        db.session.add(labeler)
        db.session.commit()
        return redirect('/crowd/index/')
        
    # START LABELING
    
    # Check if labeler still has pending labels
    if labeler.current_training_image_id !=  None:
        training_image_to_label = TrainingImage.query.filter_by(id=labeler.current_training_image_id).first()
        # Check if pending label still has to be labeled
        if training_image_to_label.total_labels < label_limit or (training_image_to_label.final_label_1 == 'Undeterminable' and labeler.labelertype == 'Expert'):
            return render_template(template, user = current_user, labeler = labeler, training_image_to_label = training_image_to_label)
        # else give him another training image
            
    # Normal procedure
    # Adjust top_n_labels if there are fewer TrainingImages
    global top_n_labels

    '''
    total_training_images = TrainingImage.query.count()
    if total_training_images < top_n_labels:
        top_n_labels = total_training_images
    
    # Get 1 random from top n labels
    training_image_to_label = TrainingImage.query.order_by(TrainingImage.total_labels.desc())[random.randrange(top_n_labels)]

    prevLabeled = TrainingImageLabel.query(image_id).filter_by(labeler_id = labeler.id) 
    availableImgs = TrainingImage.query(image_id, total_labels).outerjoin(prevLabeled,TrainingImage.image_id = prevLabeled.image_id, prevLabeled.image_id=None)
    training_image_to_label = availableImgs.query.order_by(availableImgs.total_labels.desc())[random.randrange(top_n_labels)]
    '''
    
    # IF LABELER IS AN EXPERT, PRIORITIZE GIVING Undeterminable TRAINING IMAGES
    training_images = TrainingImage.query.filter_by(final_label_1='Unlabeled').order_by(TrainingImage.total_labels.desc())[0:]
    
    undeterminable_training_images = TrainingImage.query.filter_by(final_label_1='Undeterminable')[0:]
    if labeler.labelertype == 'Expert' and len(undeterminable_training_images) > 0:
        training_image_to_label = undeterminable_training_images[0]
        
    else:
        if len(training_images) == 0:
            return render_template(template, user = current_user, labeler = labeler, training_image_to_label = None)

        for i in training_images:
            for j in i.training_image_labels:
                if j.labeler_id == labeler.id:
                    training_images.remove(i)
                    break
                    
        training_image_to_label = random.choice(training_images[:top_n_labels])
        
        # If there are no more images to label
        if training_image_to_label == None:
            return render_template(template, user = current_user, labeler = labeler, training_image_to_label = None)
            
        training_image_to_label = random.choice(training_images[:top_n_labels])
    
    # UNCOMMENT NEXT LINES TO SAVE PENDING LABEL TO LABELER
    labeler.current_training_image_id = training_image_to_label.id
    labeler.last_session = datetime.datetime.now()
    db.session.add(labeler)
    db.session.commit()
    
    return render_template(template, user = current_user, labeler = labeler, training_image_to_label = training_image_to_label)
    
@crowd.route('/crowd/login/',  methods = ['GET', 'POST'])
def login():
    form = LoginForm()
    error = False
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.query.filter_by(username=username,password=password).first()
        if user:
            login_user(user)
            return redirect("/crowd/dashboard")
        else:
            error = True
            error_message = "Invalid username or password!"
            return render_template("/crowd/index.html",login_form = LoginForm(), recovery_form = RecoveryForm(), error_message = error_message)
    else:
        error = True
    return redirect("/crowd/index")
    
@crowd.route('/crowd/logout/')
def logout():
    logout_user()
    return redirect('/crowd/index')
