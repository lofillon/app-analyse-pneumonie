import streamlit as st
import os
import json
import pandas as pd
from datetime import datetime

class DoctorView:
    """Vue pour le rôle Médecin"""
    
    def __init__(self):
        self.data_manager = st.session_state.data_manager
    
    def render(self):
        st.header("👨‍⚕️ Vue Médecin")
        
        # Navigation par onglets
        tab1, tab2, tab3 = st.tabs([
            "📋 Liste des Patients à Revoir",
            "💊 Démarrer le Traitement & Suivi",
            "📊 Résultats & Export"
        ])
        
        with tab1:
            self._render_patient_list_tab()
        
        with tab2:
            self._render_treatment_tab()
        
        with tab3:
            self._render_results_tab()
    
    def _render_patient_list_tab(self):
        """Onglet de liste des patients"""
        st.subheader("Liste Priorisée des Patients à Revoir")
        
        # Récupérer les images en attente de revue
        df = self.data_manager.get_dataframe_for_doctor()
        
        if df.empty:
            st.info("Aucun patient en attente de revue médicale")
            return
        
        st.write(f"**{len(df)} patient(s) en attente de revue**")
        
        # Statistiques
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Patients malades", len(df[df['Classification Préparateur'] == 'malade']))
        with col2:
            st.metric("Patients sains", len(df[df['Classification Préparateur'] == 'sain']))
        
        # Filtres
        st.subheader("Filtres")
        col1, col2 = st.columns(2)
        
        with col1:
            filter_classification = st.selectbox(
                "Filtrer par classification",
                ['Tous', 'malade', 'sain']
            )
        
        with col2:
            filter_priority = st.selectbox(
                "Filtrer par priorité",
                ['Toutes', 'Haute (malades)', 'Basse (sains)']
            )
        
        # Appliquer les filtres
        filtered_df = df.copy()
        
        if filter_classification != 'Tous':
            filtered_df = filtered_df[filtered_df['Classification Préparateur'] == filter_classification]
        
        if filter_priority != 'Toutes':
            if filter_priority == 'Haute (malades)':
                filtered_df = filtered_df[filtered_df['Priorité'] == 2]
            else:
                filtered_df = filtered_df[filtered_df['Priorité'] == 1]
        
        # Afficher le tableau sans mise en évidence, texte en blanc
        styled_df = filtered_df.style.set_properties(
            subset=filtered_df.columns,
            **{'color': '#ffffff'}  # Texte blanc pour toutes les lignes
        )
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Sélection d'un patient pour revue détaillée
        st.subheader("Revue Détaillée")
        
        if not filtered_df.empty:
            selected_image_id = st.selectbox(
                "Sélectionner un patient pour revue",
                filtered_df['ID Image'].tolist()
            )
            
            if selected_image_id:
                self._render_patient_detail(selected_image_id)
        else:
            st.info("Aucun patient ne correspond aux filtres")
    
    def _render_patient_detail(self, image_id):
        """Affiche la vue détaillée d'un patient"""
        image = self.data_manager.get_image(image_id)
        if not image:
            st.error("Image non trouvée")
            return
        
        patient_id = image.get('patient_id')
        patient = self.data_manager.get_patient_by_id(patient_id)
        prediction = self.data_manager.get_prediction_by_image(image_id)
        annotation = self.data_manager.get_annotation_by_image(image_id)
        
        # Informations du patient
        st.subheader(f"Patient: {patient_id}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.write(f"**Date Examen:** {image.get('exam_date', 'N/A')}")
        with col2:
            if patient:
                st.write(f"**Sexe:** {patient.get('metadata', {}).get('sex', 'N/A')}")
        with col3:
            if patient:
                st.write(f"**Âge:** {patient.get('metadata', {}).get('age', 'N/A')}")
        with col4:
            st.write(f"**Position:** {image.get('patient_position', 'N/A')}")
        
        # Afficher l'image
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("Radiographie")
            image_path = image.get('image_path')
            if image_path and os.path.exists(image_path):
                st.image(image_path, use_container_width=True)
            else:
                st.warning("Image non disponible")
        
        with col2:
            st.subheader("Informations")
            
            # Prédiction du modèle
            if prediction:
                st.write("**Prédiction Modèle:**")
                if prediction.get('label') == 'malade':
                    st.error(f"🔴 {prediction.get('label')}")
                else:
                    st.success(f"🟢 {prediction.get('label')}")
            
            # Classification du préparateur
            if annotation and annotation.get('user_role') == 'Préparateur':
                st.write("**Classification Préparateur:**")
                if annotation.get('label') == 'malade':
                    st.error(f"🔴 {annotation.get('label')}")
                else:
                    st.success(f"🟢 {annotation.get('label')}")
                st.write(f"**Par:** {annotation.get('user_name', 'N/A')}")
                st.write(f"**Version:** {annotation.get('version', 1)}")
                
                if annotation.get('notes'):
                    st.write("**Notes Préparateur:**")
                    st.info(annotation.get('notes'))
            
            # Informations supplémentaires
            if annotation and annotation.get('additional_info'):
                info = annotation.get('additional_info', {})
                st.write("**Informations Complémentaires:**")
                
                if info.get('symptoms'):
                    st.write(f"**Symptômes:** {info.get('symptoms')}")
                if info.get('comorbidities'):
                    st.write(f"**Comorbidités:** {info.get('comorbidities')}")
                if info.get('spo2'):
                    st.write(f"**SpO₂:** {info.get('spo2')}%")
                if info.get('temperature'):
                    st.write(f"**Température:** {info.get('temperature')}°C")
                if info.get('crp'):
                    st.write(f"**CRP:** {info.get('crp')} mg/L")
                if info.get('image_quality'):
                    st.write(f"**Qualité image:** {info.get('image_quality')}")
                if info.get('urgency'):
                    urgency_color = {
                        'Normale': '🟢',
                        'Élevée': '🟡',
                        'Critique': '🔴'
                    }
                    st.write(f"**Urgence:** {urgency_color.get(info.get('urgency'), '')} {info.get('urgency')}")
        
        # Formulaire de validation/correction
        st.subheader("Validation Clinique")
        
        with st.form(f"validation_form_{image_id}"):
            # Récupérer la classification actuelle
            current_label = 'sain'
            if annotation:
                # Vérifier s'il y a déjà une validation médicale
                medical_annotations = [a for a in self.data_manager.get_all_annotations() 
                                     if a.get('image_id') == image_id and a.get('user_role') == 'Médecin']
                if medical_annotations:
                    latest_medical = max(medical_annotations, key=lambda x: x.get('version', 0))
                    current_label = latest_medical.get('label', annotation.get('label', 'sain'))
                else:
                    current_label = annotation.get('label', 'sain')
            
            # Label de diagnostic final
            final_label = st.radio(
                "Diagnostic Final",
                ['sain', 'malade'],
                index=0 if current_label == 'sain' else 1,
                help="Classification finale basée sur votre jugement clinique"
            )
            
            # Confiance du médecin
            medical_confidence = st.slider(
                "Confiance du diagnostic",
                min_value=0.0,
                max_value=1.0,
                value=0.9,
                step=0.01
            )
            
            # Commentaire clinique
            clinical_notes = st.text_area(
                "Commentaire clinique",
                placeholder="Ajoutez vos observations cliniques, raisonnement, etc."
            )
            
            # Résultat clinique réel (après traitement)
            st.subheader("Résultat Clinique Réel (après traitement)")
            st.info("À compléter après le traitement ou le suivi du patient")
            
            ground_truth = st.radio(
                "Vérité terrain finale",
                ['Non déterminé', 'Pneumonie confirmée', 'Absence de pneumonie'],
                help="Résultat réel après traitement/suivi"
            )
            
            ground_truth_label = None
            if ground_truth == 'Pneumonie confirmée':
                ground_truth_label = 'malade'
            elif ground_truth == 'Absence de pneumonie':
                ground_truth_label = 'sain'
            
            result_notes = st.text_area(
                "Notes de résultat",
                placeholder="Détails sur le résultat final, traitement administré, etc."
            )
            
            submitted = st.form_submit_button("✅ Valider le Diagnostic", type="primary")
            
            if submitted:
                # Créer ou mettre à jour l'annotation médicale
                medical_annotation_data = {
                    'label': final_label,
                    'confidence': medical_confidence,
                    'notes': clinical_notes,
                    'user_role': 'Médecin',
                    'additional_info': {
                        'ground_truth': ground_truth_label,
                        'ground_truth_notes': result_notes,
                        'validated_at': datetime.now().isoformat()
                    }
                }
                
                # Vérifier s'il existe déjà une annotation médicale
                medical_annotations = [a for a in self.data_manager.get_all_annotations() 
                                     if a.get('image_id') == image_id and a.get('user_role') == 'Médecin']
                
                if medical_annotations:
                    # Mettre à jour
                    self.data_manager.update_annotation(
                        image_id,
                        st.session_state.current_user_name,
                        medical_annotation_data
                    )
                else:
                    # Créer
                    self.data_manager.add_annotation({
                        'image_id': image_id,
                        'patient_id': patient_id,
                        **medical_annotation_data,
                        'user_name': st.session_state.current_user_name
                    })
                
                st.success("✅ Diagnostic validé et enregistré")
                st.rerun()
        
        # Section pour démarrer le traitement
        st.divider()
        st.subheader("💊 Démarrer le Traitement")
        
        # Vérifier si un traitement existe déjà
        existing_treatment = annotation.get('additional_info', {}).get('treatment') if annotation else None
        
        if existing_treatment:
            st.info(f"**Traitement en cours:** {existing_treatment.get('action_type', 'N/A').title()} - Statut: {existing_treatment.get('status', 'N/A')}")
            st.write(f"**Démarré le:** {existing_treatment.get('started_at', 'N/A')}")
            if existing_treatment.get('details', {}).get('notes'):
                st.write(f"**Notes:** {existing_treatment.get('details', {}).get('notes')}")
        else:
            # Bouton pour démarrer un traitement
            if st.button("🚀 Démarrer un Traitement", type="primary"):
                st.session_state.start_treatment_for = image_id
                st.info("💡 Allez dans l'onglet '💊 Démarrer le Traitement & Suivi' pour compléter le formulaire")
                st.rerun()
        
        # Historique des modifications
        st.subheader("Historique des Modifications")
        audit_log = self.data_manager.get_audit_log(image_id)
        
        if audit_log:
            for entry in sorted(audit_log, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]:
                st.write(f"**{entry.get('timestamp', 'N/A')}** - {entry.get('user_name', 'N/A')}")
                st.write(f"Action: {entry.get('action', 'N/A')}")
                details = entry.get('details', {})
                if 'old_label' in details and 'new_label' in details:
                    st.write(f"Changement: {details.get('old_label')} → {details.get('new_label')}")
                st.divider()
        else:
            st.info("Aucun historique disponible")
    
    def _render_treatment_tab(self):
        """Onglet pour démarrer le traitement et suivre les patients"""
        st.subheader("💊 Démarrer le Traitement et Liste de Suivi")
        
        # Section 1: Démarrer un traitement
        st.subheader("🚀 Démarrer un Traitement")
        
        # Récupérer les patients validés par le médecin (pas encore en traitement)
        images = self.data_manager.get_all_images()
        medical_annotations = {a.get('image_id'): a for a in self.data_manager.get_all_annotations() 
                              if a.get('user_role') == 'Médecin'}
        
        validated_patients = []
        for img in images:
            if img['id'] in medical_annotations:
                ann = medical_annotations[img['id']]
                # Vérifier si pas déjà en traitement
                if not ann.get('additional_info', {}).get('treatment'):
                    validated_patients.append({
                        'image': img,
                        'annotation': ann
                    })
        
        if not validated_patients:
            st.info("Aucun patient validé disponible pour démarrer un traitement")
        else:
            st.write(f"**{len(validated_patients)} patient(s) validé(s) disponible(s)**")
            
            # Sélection d'un patient
            patient_options = {
                f"{p['image'].get('patient_id', 'N/A')} - {p['image'].get('exam_date', 'N/A')}": p['image']['id']
                for p in validated_patients
            }
            
            # Si on vient de la vue détaillée, pré-sélectionner le patient
            default_index = 0
            if 'start_treatment_for' in st.session_state and st.session_state.start_treatment_for:
                target_id = st.session_state.start_treatment_for
                for idx, (label, img_id) in enumerate(patient_options.items()):
                    if img_id == target_id:
                        default_index = idx
                        break
                # Nettoyer la variable de session après utilisation
                del st.session_state.start_treatment_for
            
            selected_patient_label = st.selectbox(
                "Sélectionner un patient pour démarrer le traitement",
                list(patient_options.keys()),
                index=default_index
            )
            
            if selected_patient_label:
                selected_image_id = patient_options[selected_patient_label]
                selected_patient = next(p for p in validated_patients if p['image']['id'] == selected_image_id)
                
                # Afficher les informations du patient
                image = selected_patient['image']
                annotation = selected_patient['annotation']
                patient_id = image.get('patient_id')
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**ID Patient:** {patient_id}")
                    st.write(f"**Date Examen:** {image.get('exam_date', 'N/A')}")
                with col2:
                    st.write(f"**Diagnostic:** {annotation.get('label', 'N/A')}")
                    st.write(f"**Validé par:** {annotation.get('user_name', 'N/A')}")
                
                # Formulaire pour démarrer le traitement
                with st.form("start_treatment_form"):
                    st.subheader("Type d'Action")
                    
                    action_type = st.radio(
                        "Sélectionner le type d'action",
                        ['prescription', 'examens', 'hospitalisation', 'orientation'],
                        help="Choisissez l'action à entreprendre pour ce patient"
                    )
                    
                    # Détails selon le type d'action
                    details = {}
                    
                    if action_type == 'prescription':
                        st.subheader("Détails de la Prescription")
                        details['medication'] = st.text_input("Médicament(s)", placeholder="Ex: Amoxicilline 500mg")
                        details['dosage'] = st.text_input("Posologie", placeholder="Ex: 3x par jour pendant 7 jours")
                        details['duration'] = st.number_input("Durée (jours)", min_value=1, value=7)
                    
                    elif action_type == 'examens':
                        st.subheader("Examens Complémentaires")
                        exam_types = st.multiselect(
                            "Type d'examen(s)",
                            ['Scanner thoracique', 'Prise de sang', 'ECG', 'Échographie', 'Autre']
                        )
                        details['exam_types'] = exam_types
                        if 'Autre' in exam_types:
                            details['other_exam'] = st.text_input("Préciser l'autre examen")
                        details['urgency'] = st.selectbox(
                            "Urgence",
                            ['Normale', 'Urgente', 'Très urgente']
                        )
                    
                    elif action_type == 'hospitalisation':
                        st.subheader("Détails d'Hospitalisation")
                        details['department'] = st.selectbox(
                            "Service",
                            ['Médecine', 'Soins intensifs', 'Urgences', 'Pneumologie', 'Autre']
                        )
                        details['reason'] = st.text_area("Motif d'hospitalisation")
                        details['estimated_duration'] = st.number_input("Durée estimée (jours)", min_value=1, value=3)
                    
                    elif action_type == 'orientation':
                        st.subheader("Orientation")
                        details['destination'] = st.selectbox(
                            "Orienter vers",
                            ['Médecin spécialiste', 'Service hospitalier', 'Soins à domicile', 'Suivi ambulatoire', 'Autre']
                        )
                        details['reason'] = st.text_area("Motif d'orientation")
                    
                    notes = st.text_area("Notes complémentaires", placeholder="Ajoutez des notes sur le traitement...")
                    if notes:
                        details['notes'] = notes
                    
                    submitted = st.form_submit_button("✅ Démarrer le Traitement", type="primary")
                    
                    if submitted:
                        self.data_manager.start_treatment(
                            selected_image_id,
                            st.session_state.current_user_name,
                            action_type,
                            details
                        )
                        st.success(f"✅ Traitement démarré pour le patient {patient_id}")
                        st.rerun()
        
        # Section 2: Liste de suivi des patients en traitement
        st.divider()
        st.subheader("📋 Liste de Suivi des Patients en Traitement")
        
        patients_in_treatment = self.data_manager.get_patients_in_treatment()
        
        if not patients_in_treatment:
            st.info("Aucun patient en traitement pour le moment")
        else:
            st.write(f"**{len(patients_in_treatment)} patient(s) en traitement**")
            
            # Statistiques
            col1, col2, col3 = st.columns(3)
            with col1:
                en_traitement = len([p for p in patients_in_treatment if p['treatment'].get('status') == 'en_traitement'])
                st.metric("En traitement", en_traitement)
            with col2:
                en_attente = len([p for p in patients_in_treatment if p['treatment'].get('status') == 'en_attente_examens'])
                st.metric("En attente d'examens", en_attente)
            with col3:
                hospitalises = len([p for p in patients_in_treatment if p['treatment'].get('status') == 'hospitalise'])
                st.metric("Hospitalisés", hospitalises)
            
            # Liste des patients
            for patient_data in patients_in_treatment:
                image = patient_data['image']
                annotation = patient_data['annotation']
                treatment = patient_data['treatment']
                
                with st.expander(f"Patient {image.get('patient_id', 'N/A')} - {treatment.get('action_type', 'N/A').title()} - {treatment.get('status', 'N/A')}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write(f"**ID Patient:** {image.get('patient_id', 'N/A')}")
                        st.write(f"**Date Examen:** {image.get('exam_date', 'N/A')}")
                        st.write(f"**Diagnostic:** {annotation.get('label', 'N/A')}")
                    
                    with col2:
                        st.write(f"**Type d'action:** {treatment.get('action_type', 'N/A').title()}")
                        st.write(f"**Statut:** {treatment.get('status', 'N/A')}")
                        st.write(f"**Démarré le:** {treatment.get('started_at', 'N/A')}")
                        st.write(f"**Par:** {treatment.get('started_by', 'N/A')}")
                    
                    # Afficher les détails selon le type
                    st.subheader("Détails du Traitement")
                    details = treatment.get('details', {})
                    
                    if treatment.get('action_type') == 'prescription':
                        st.write(f"**Médicament:** {details.get('medication', 'N/A')}")
                        st.write(f"**Posologie:** {details.get('dosage', 'N/A')}")
                        st.write(f"**Durée:** {details.get('duration', 'N/A')} jours")
                    
                    elif treatment.get('action_type') == 'examens':
                        st.write(f"**Examens demandés:** {', '.join(details.get('exam_types', []))}")
                        if details.get('other_exam'):
                            st.write(f"**Autre examen:** {details.get('other_exam')}")
                        st.write(f"**Urgence:** {details.get('urgency', 'N/A')}")
                    
                    elif treatment.get('action_type') == 'hospitalisation':
                        st.write(f"**Service:** {details.get('department', 'N/A')}")
                        st.write(f"**Motif:** {details.get('reason', 'N/A')}")
                        st.write(f"**Durée estimée:** {details.get('estimated_duration', 'N/A')} jours")
                    
                    elif treatment.get('action_type') == 'orientation':
                        st.write(f"**Destination:** {details.get('destination', 'N/A')}")
                        st.write(f"**Motif:** {details.get('reason', 'N/A')}")
                    
                    if details.get('notes'):
                        st.write(f"**Notes:** {details.get('notes')}")
                    
                    # Mise à jour du statut
                    st.subheader("Mettre à jour le Statut")
                    with st.form(f"update_status_form_{image['id']}"):
                        new_status = st.selectbox(
                            "Nouveau statut",
                            ['en_traitement', 'en_attente_examens', 'hospitalise', 'termine'],
                            index=['en_traitement', 'en_attente_examens', 'hospitalise', 'termine'].index(treatment.get('status', 'en_traitement')),
                            key=f"status_{image['id']}"
                        )
                        
                        status_notes = st.text_area(
                            "Notes sur le changement de statut",
                            key=f"status_notes_{image['id']}"
                        )
                        
                        if st.form_submit_button("💾 Mettre à jour le Statut", type="primary"):
                            self.data_manager.update_treatment_status(
                                image['id'],
                                st.session_state.current_user_name,
                                new_status,
                                status_notes
                            )
                            st.success("✅ Statut mis à jour")
                            st.rerun()
    
    def _render_results_tab(self):
        """Onglet de résultats et export"""
        st.subheader("Résultats Finalisés et Export")
        
        # Récupérer les images validées par le médecin
        images = self.data_manager.get_all_images()
        medical_annotations = {a.get('image_id'): a for a in self.data_manager.get_all_annotations() 
                              if a.get('user_role') == 'Médecin'}
        
        validated_images = []
        for img in images:
            if img['id'] in medical_annotations:
                validated_images.append({
                    'image': img,
                    'annotation': medical_annotations[img['id']]
                })
        
        if not validated_images:
            st.info("Aucun patient validé pour le moment")
            return
        
        st.write(f"**{len(validated_images)} patient(s) validé(s)**")
        
        # Statistiques
        confirmed_sick = sum(1 for v in validated_images if v['annotation'].get('label') == 'malade')
        confirmed_healthy = sum(1 for v in validated_images if v['annotation'].get('label') == 'sain')
        
        col1, col2 = st.columns(2)
        col1.metric("Pneumonie confirmée", confirmed_sick)
        col2.metric("Absence de pneumonie", confirmed_healthy)
        
        # Liste des patients validés
        st.subheader("Liste des Patients Validés")
        
        df_results = pd.DataFrame([{
            'ID Image': v['image']['id'],
            'ID Patient': v['image'].get('patient_id', 'N/A'),
            'Date Examen': v['image'].get('exam_date', 'N/A'),
            'Diagnostic Final': v['annotation'].get('label', 'N/A'),
            'Confiance': v['annotation'].get('confidence', 0.0),
            'Vérité Terrain': v['annotation'].get('additional_info', {}).get('ground_truth', 'Non déterminé'),
            'Validé par': v['annotation'].get('user_name', 'N/A'),
            'Date Validation': v['annotation'].get('created_at', 'N/A')
        } for v in validated_images])
        
        st.dataframe(df_results, use_container_width=True)
        
        # Sélection des patients à finaliser
        st.subheader("Finalisation du Lot")
        
        selected_images = st.multiselect(
            "Sélectionner les patients à finaliser",
            [v['image']['id'] for v in validated_images],
            default=[v['image']['id'] for v in validated_images]
        )
        
        if st.button("✅ Marquer comme Finalisé", type="primary"):
            self.data_manager.mark_batch_finalized(
                selected_images,
                st.session_state.current_user_name
            )
            st.success(f"✅ {len(selected_images)} patient(s) marqué(s) comme finalisé(s)")
            st.rerun()
        
        # Export pour entraînement
        st.subheader("Export pour Entraînement")
        
        finalized_images = [img for img in images if img.get('status') == 'finalized']
        
        if finalized_images:
            st.write(f"**{len(finalized_images)} patient(s) finalisé(s) disponible(s) pour export**")
            
            # Résumé de ce qui sera exporté
            finalized_annotations = {}
            for img in finalized_images:
                ann = self.data_manager.get_annotation_by_image(img['id'])
                if ann and ann.get('user_role') == 'Médecin':
                    finalized_annotations[img['id']] = ann
            
            if finalized_annotations:
                labels_changed = 0
                for img_id, ann in finalized_annotations.items():
                    img = self.data_manager.get_image(img_id)
                    pred = self.data_manager.get_prediction_by_image(img_id)
                    if pred and pred.get('label') != ann.get('label'):
                        labels_changed += 1
                
                st.info(f"""
                **Résumé de l'export:**
                - Nombre de cas: {len(finalized_annotations)}
                - Étiquettes modifiées: {labels_changed}
                - Pneumonie confirmée: {sum(1 for a in finalized_annotations.values() if a.get('label') == 'malade')}
                - Absence de pneumonie: {sum(1 for a in finalized_annotations.values() if a.get('label') == 'sain')}
                """)
                
                if st.button("📥 Préparer l'Export pour Entraînement", type="primary"):
                    # Préparer les données pour l'export
                    export_data = []
                    for img_id, ann in finalized_annotations.items():
                        img = self.data_manager.get_image(img_id)
                        export_data.append({
                            'image_id': img_id,
                            'image_path': img.get('image_path'),
                            'patient_id': img.get('patient_id'),
                            'final_label': ann.get('label'),
                            'ground_truth': ann.get('additional_info', {}).get('ground_truth'),
                            'confidence': ann.get('confidence'),
                            'notes': ann.get('notes', ''),
                            'validated_by': ann.get('user_name'),
                            'validated_at': ann.get('created_at')
                        })
                    
                    # Sauvegarder dans un fichier JSON
                    import json
                    export_file = "data/export_training_data.json"
                    os.makedirs("data", exist_ok=True)
                    with open(export_file, 'w', encoding='utf-8') as f:
                        json.dump(export_data, f, indent=2, ensure_ascii=False, default=str)
                    
                    st.success(f"✅ Données exportées dans {export_file}")
                    st.download_button(
                        label="📥 Télécharger le fichier d'export",
                        data=json.dumps(export_data, indent=2, ensure_ascii=False, default=str),
                        file_name=f"training_data_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                        mime="application/json"
                    )
        else:
            st.info("Aucun patient finalisé pour le moment")

