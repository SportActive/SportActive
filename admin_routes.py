from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func
import json

# Імпортуємо 'db' та моделі з нашого основного файлу app.py
from app import db, FinancialTransaction, Announcement, Poll, GameLog, User

# Створюємо Blueprint з назвою 'admin'
admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/finances', methods=['GET', 'POST'])
@login_required
def finances():
    if not current_user.can_view_finances():
        flash('Доступ заборонено.', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        if not current_user.can_edit_finances():
            flash('У вас немає дозволу на цю дію.', 'error')
            return redirect(url_for('admin.finances'))
        form_type = request.form.get('form_type')
        if form_type == 'add_transaction':
            try:
                amount = float(request.form.get('amount'))
                trans_type = request.form.get('transaction_type')
                new_transaction = FinancialTransaction(
                    description=request.form.get('description'),
                    date=request.form.get('date'),
                    amount=-amount if trans_type == 'expense' else amount,
                    transaction_type=trans_type,
                    logged_by_admin=current_user.username,
                    logged_at=datetime.utcnow()
                )
                db.session.add(new_transaction)
                db.session.commit()
                flash('Транзакцію успішно додано!', 'success')
            except (ValueError, TypeError):
                flash('Невірний формат суми.', 'error')
        elif form_type == 'update_user_fee':
            user = User.query.get(request.form.get('user_id'))
            if user:
                try:
                    fee_amount = float(request.form.get('fee_amount'))
                    payment_period = request.form.get('payment_period')
                    fee_description = f"Членський внесок ({payment_period}) від {user.username}"
                    new_fee = FinancialTransaction(
                        description=fee_description,
                        date=request.form.get('fee_date'),
                        amount=fee_amount,
                        transaction_type='income',
                        logged_by_admin=current_user.nickname or current_user.username,
                        logged_at=datetime.utcnow()
                    )
                    db.session.add(new_fee)
                    db.session.commit()
                    flash(f'Внесок для {user.nickname or user.username} успішно оновлено.', 'success')
                except (ValueError, TypeError):
                    flash('Невірний формат суми внеску.', 'error')
        return redirect(url_for('admin.finances', period=request.args.get('period', '')))

    period = request.args.get('period', datetime.now().strftime('%Y-%m'))
    try:
        start_of_month = datetime.strptime(period, '%Y-%m')
    except ValueError:
        period = datetime.now().strftime('%Y-%m')
        start_of_month = datetime.strptime(period, '%Y-%m')
        
    end_of_month = (start_of_month.replace(day=28) + timedelta(days=4)).replace(day=1)
    
    start_balance = db.session.query(func.sum(FinancialTransaction.amount)).filter(FinancialTransaction.date < start_of_month.strftime('%Y-%m-%d')).scalar() or 0.0
    transactions = FinancialTransaction.query.filter(FinancialTransaction.date >= start_of_month.strftime('%Y-%m-%d'), FinancialTransaction.date < end_of_month.strftime('%Y-%m-%d')).order_by(FinancialTransaction.date.desc()).all()
    
    total_income = sum(t.amount for t in transactions if t.transaction_type == 'income')
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == 'expense')
    end_balance = start_balance + total_income + total_expenses
    
    summary = {'start_balance': round(start_balance, 2), 'total_income': round(total_income, 2), 'total_expenses': round(abs(total_expenses), 2), 'end_balance': round(end_balance, 2)}
    users = User.query.order_by(User.username).all()
    
    paid_users_for_period = {t.description.split(' від ')[-1] for t in FinancialTransaction.query.filter(FinancialTransaction.description.like(f"%Членський внесок ({period})%")).all() if ' від ' in t.description}
    
    return render_template('finances.html', users=users, transactions=transactions, summary=summary, period_filter=period, paid_users_for_period=paid_users_for_period)

@admin_bp.route('/edit_transaction/<int:transaction_id>', methods=['GET', 'POST'])
@login_required
def edit_transaction(transaction_id):
    if not current_user.can_edit_finances():
        flash('У вас немає дозволу на цю дію.', 'error')
        return redirect(url_for('admin.finances'))
    transaction = FinancialTransaction.query.get_or_404(transaction_id)
    if request.method == 'POST':
        try:
            amount = float(request.form.get('amount'))
            transaction.description = request.form.get('description')
            transaction.date = request.form.get('date')
            transaction.transaction_type = request.form.get('transaction_type')
            transaction.amount = -amount if transaction.transaction_type == 'expense' else amount
            db.session.commit()
            flash('Транзакцію успішно оновлено!', 'success')
            return redirect(url_for('admin.finances'))
        except (ValueError, TypeError):
            flash('Невірний формат суми.', 'error')
    transaction.form_amount = abs(transaction.amount)
    return render_template('edit_transaction.html', transaction=transaction)

@admin_bp.route('/delete_transaction/<int:transaction_id>', methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    if not current_user.can_edit_finances():
        flash('У вас немає дозволу на цю дію.', 'error')
        return redirect(url_for('admin.finances'))
    transaction = FinancialTransaction.query.get_or_404(transaction_id)
    db.session.delete(transaction)
    db.session.commit()
    flash('Транзакцію успішно видалено.', 'success')
    return redirect(url_for('admin.finances'))

@admin_bp.route('/update_user_role/<int:user_id>', methods=['POST'])
@login_required
def update_user_role(user_id):
    if not current_user.is_admin():
        flash('Тільки адміністратор може змінювати ролі.', 'error')
        return redirect(url_for('admin.finances'))
    user_to_update = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    if new_role in ['user', 'superuser', 'admin']:
        if user_to_update.id == current_user.id and user_to_update.is_admin() and new_role != 'admin':
            if User.query.filter_by(role='admin').count() <= 1:
                flash('Ви не можете змінити роль єдиного адміністратора.', 'error')
                return redirect(url_for('admin.finances'))
        user_to_update.role = new_role
        db.session.commit()
        flash(f'Роль для {user_to_update.nickname or user_to_update.username} оновлено на "{new_role}".', 'success')
    else:
        flash('Неприпустима роль.', 'error')
    return redirect(url_for('admin.finances'))

@admin_bp.route('/announcements', methods=['GET', 'POST'])
@login_required
def announcements():
    if request.method == 'POST':
        if not current_user.can_manage_events(): # Перевірка прав на створення
            flash('У вас немає дозволу.', 'error')
            return redirect(url_for('admin.announcements'))
        title = request.form['title']
        content = request.form['content']
        if title and content:
            new_announcement = Announcement(title=title, content=content, date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), author=current_user.nickname or current_user.username)
            db.session.add(new_announcement)
            db.session.commit()
            flash('Оголошення успішно додано!', 'success')
        else:
            flash('Будь ласка, заповніть усі поля.', 'error')
        return redirect(url_for('admin.announcements'))
    
    all_announcements = Announcement.query.order_by(Announcement.date.desc()).all()
    if current_user.is_authenticated:
        seen_items = current_user.seen_items
        seen_ids = set(seen_items.get('announcements', []))
        ids_on_page = {a.id for a in all_announcements}
        if not ids_on_page.issubset(seen_ids):
            seen_ids.update(ids_on_page)
            seen_items['announcements'] = list(seen_ids)
            current_user.seen_items = seen_items
            db.session.commit()

    return render_template('announcements.html', announcements=all_announcements)

@admin_bp.route('/edit_announcement/<int:announcement_id>', methods=['GET', 'POST'])
@login_required
def edit_announcement(announcement_id):
    if not current_user.can_manage_events():
        flash('У вас немає дозволу на редагування.', 'error')
        return redirect(url_for('admin.announcements'))
    announcement = Announcement.query.get_or_404(announcement_id)
    if request.method == 'POST':
        announcement.title = request.form['title']
        announcement.content = request.form['content']
        db.session.commit()
        flash('Оголошення успішно оновлено!', 'success')
        return redirect(url_for('admin.announcements'))
    return render_template('edit_announcement.html', announcement=announcement)

@admin_bp.route('/delete_announcement/<int:announcement_id>', methods=['POST'])
@login_required
def delete_announcement(announcement_id):
    if not current_user.can_manage_events():
        flash('У вас немає дозволу на видалення.', 'error')
        return redirect(url_for('admin.announcements'))
    announcement = Announcement.query.get_or_404(announcement_id)
    db.session.delete(announcement)
    db.session.commit()
    flash('Оголошення успішно видалено!', 'success')
    return redirect(url_for('admin.announcements'))

@admin_bp.route('/polls', methods=['GET', 'POST'])
@login_required
def polls():
    if request.method == 'POST':
        if not current_user.can_manage_events(): # Перевірка прав на створення
            flash('У вас немає дозволу на створення опитувань.', 'error')
            return redirect(url_for('admin.polls'))
        question = request.form['question']
        options_raw = [opt.strip() for opt in request.form.getlist('options[]') if opt.strip()]
        if not question or not options_raw:
            flash('Будь ласка, заповніть питання та хоча б один варіант.', 'error')
        else:
            options_for_save = [{'text': opt, 'votes': 0} for opt in options_raw]
            new_poll = Poll(question=question, options_json=json.dumps(options_for_save, ensure_ascii=False), date=datetime.now().strftime('%Y-%m-%d %H:%M:%S'), author=current_user.nickname or current_user.username)
            db.session.add(new_poll)
            db.session.commit()
            flash('Опитування успішно створено!', 'success')
        return redirect(url_for('admin.polls'))
    
    all_polls = Poll.query.order_by(Poll.date.desc()).all()
    if current_user.is_authenticated:
        seen_items = current_user.seen_items
        seen_ids = set(seen_items.get('polls', []))
        ids_on_page = {p.id for p in all_polls}
        if not ids_on_page.issubset(seen_ids):
            seen_ids.update(ids_on_page)
            seen_items['polls'] = list(seen_ids)
            current_user.seen_items = seen_items
            db.session.commit()
            
    return render_template('polls.html', polls=all_polls)

@admin_bp.route('/vote_poll/<int:poll_id>', methods=['POST'])
@login_required
def vote_poll(poll_id):
    poll = Poll.query.get_or_404(poll_id)
    if current_user.username in poll.voted_users:
        flash('Ви вже проголосували в цьому опитуванні.', 'info')
        return redirect(url_for('admin.polls'))
    
    vote_option_index = request.form.get('option')
    if vote_option_index:
        try:
            option_index = int(vote_option_index)
            options = poll.options
            if 0 <= option_index < len(options):
                options[option_index]['votes'] += 1
                poll.options = options
                
                voted_users = poll.voted_users
                voted_users.append(current_user.username)
                poll.voted_users = voted_users
                
                db.session.commit()
                flash('Ваш голос зараховано!', 'success')
            else:
                flash('Недійсний варіант голосування.', 'error')
        except (ValueError, TypeError):
            flash('Невірний запит.', 'error')
    else:
        flash('Будь ласка, оберіть варіант.', 'error')
        
    return redirect(url_for('admin.polls'))

@admin_bp.route('/delete_poll/<int:poll_id>', methods=['POST'])
@login_required
def delete_poll(poll_id):
    if not current_user.can_manage_events():
        flash('У вас немає дозволу на видалення.', 'error')
        return redirect(url_for('admin.polls'))
    poll = Poll.query.get_or_404(poll_id)
    db.session.delete(poll)
    db.session.commit()
    flash('Опитування успішно видалено!', 'success')
    return redirect(url_for('admin.polls'))

@admin_bp.route('/game_log')
@login_required
def game_log():
    if not current_user.can_manage_events():
        flash('Доступ заборонено.', 'error')
        return redirect(url_for('index'))
    period_filter = request.args.get('period', '').strip()
    query = GameLog.query
    if period_filter:
        query = query.filter(GameLog.event_date.like(f"{period_filter}%"))
    game_logs = query.order_by(GameLog.logged_at.desc()).all()
    return render_template('game_log.html', game_logs=game_logs, period_filter=period_filter)