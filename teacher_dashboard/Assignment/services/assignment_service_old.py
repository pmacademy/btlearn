from teacher_dashboard.Assignment.daos.assignment_student_dao import assignment_student_dao
from teacher_dashboard.Assignment.services.classroom_service_old import classroom_service
from teacher_dashboard.models import Assignment, AssignmentQuestion, AssignmentClass, AssignmentStudent, AssignmentStudentQuestion
from teacher_dashboard.Assignment.daos.assignment_dao import assignment_dao
from teacher_dashboard.Assignment.schemas.assignment_schema_old import AllAssignmentStudentResponse, AllAssignmentTeacherResponse, AssignmentTopics, BasicAssignementDetailsStudentResponse, BasicAssignementDetailsTeacherResponse, CreateAssignmentRequest, UpdateAssignmentPublishStatusRequest, UpdateAssignmentRequest, AssignmentResponse, AssignmentQuestionSchema
from fastapi.exceptions import HTTPException
from teacher_dashboard.db_session import DatabaseSession
from teacher_dashboard.Assignment.constants.enums import AssignmentStatusEnum, QuestionStatusEnum
from datetime import datetime
from typing import List
from sqlalchemy.sql.expression import update
from sqlalchemy.sql.functions import user


class AssignmentService:
    def get_assignment(self, assignment_id: int):
        assignment_in_db = assignment_dao.find_by_id(assignment_id)

        if(assignment_in_db == None):
            raise HTTPException(
                401, detail="No assignment exists with the given id")

        # if(assignment_in_db.teacher_id != user_id):
        #     raise HTTPException(
        #         401, detail="Not authorized to access the assignment.")

        return self.__get_formatted_assignment(assignment_in_db)

    def __get_formatted_assignment(self, assignment_in_db):
        questions_in_db = assignment_in_db.questions
        topics = []
        for q in questions_in_db:
            if(len(topics) > 0 and topics[-1].topic_sequence_num == q.topic_sequence_num and topics[-1].topic_code == q.topic_code):
                topics[-1].questions.append(AssignmentQuestionSchema(
                    question_id=q.question_id,
                    sequence_num=q.sequence_num,
                    tutor_available=q.tutor_available
                ))
            else:
                topics.append(AssignmentTopics(
                    topic_code=q.topic_code,
                    topic_sequence_num=q.topic_sequence_num,
                    topic_tutor_available=q.topic_tutor_available,
                    questions=[AssignmentQuestionSchema(
                        question_id=q.question_id,
                        sequence_num=q.sequence_num,
                        tutor_available=q.tutor_available
                    )]
                ))
        return AssignmentResponse(
            id=assignment_in_db.id,
            teacher_id=assignment_in_db.teacher_id,
            title=assignment_in_db.title,
            classes=assignment_in_db.classes,
            is_published=assignment_in_db.is_published,
            submission_last_date=assignment_in_db.submission_last_date,
            last_modified_time=assignment_in_db.updated_at,
            topics=topics
        )

    def get_all_teacher_assignments(self, user_id: str):
        # validate teacher_id
        all_assignments_in_db = assignment_dao.find_by_teacher_id(user_id)

        if(len(all_assignments_in_db) == 0):
            raise HTTPException(
                401, detail="No assignment exists for the given teacher_id")

        published = []
        not_published = []

        for assignment in all_assignments_in_db:

            completed_count = 0
            for student in assignment.students:
                if(student.status != QuestionStatusEnum.NOT_ATTEMPTED):
                    completed_count += 1
            total_count = len(assignment.students)

            completetion_status = "{completed_count}/{total_count}".format(
                completed_count=completed_count, total_count=total_count)

            response_assignment = BasicAssignementDetailsTeacherResponse(id=assignment.id,
                                                                         title=assignment.title,
                                                                         classes_count=len(
                                                                             assignment.classes),
                                                                         completion_status=completetion_status,
                                                                         questions_count=len(
                                                                             assignment.questions),
                                                                         is_published=assignment.is_published,
                                                                         submission_last_date=assignment.submission_last_date,
                                                                         last_modified_time=assignment.updated_at,
                                                                         performance=0)
            if(response_assignment.is_published == True):
                published.append(response_assignment)
            else:
                not_published.append(response_assignment)

        published.sort(key=lambda assign: assign.submission_last_date)
        not_published.sort(
            key=lambda assign: assign.last_modified_time, reverse=True)

        return AllAssignmentTeacherResponse(teacher_id=user_id,
                                            published=published,
                                            not_published=not_published)

    def create_assignment(self, assignment: CreateAssignmentRequest):
        # todo: add class validation
        # todo: add student validation
        # todo: assignment default deadline
        # todo: tesacher_id validation
        # todo: check if is_published=True & deadline!=None

        assignment_question_list = []

        for topic in assignment.topics:
            for ques in topic.questions:
                assignment_question_list.append(AssignmentQuestion(
                    question_id=ques.question_id,
                    sequence_num=ques.sequence_num,
                    tutor_available=ques.tutor_available,
                    topic_code=topic.topic_code,
                    topic_sequence_num=topic.topic_sequence_num,
                    cluster_id="",
                    topic_tutor_available=topic.tutor_available
                ))

        assignment_classes_list = [AssignmentClass(class_id=i.class_id)
                                   for i in assignment.classes]

        assignment_students_list = []
        for class_item in assignment.classes:
            class_students = classroom_service.get_students(
                class_item.class_id)
            for student in class_students:
                assignment_students_list.append(
                    AssignmentStudent(
                        student_id=student["id"],
                        class_id=student["class_id"],
                        first_name=student["first_name"],
                        last_name=student["last_name"],
                        email=student["email"],
                        parents_email=student["parents_email"],
                        questions=[AssignmentStudentQuestion(
                            question_id=ques.question_id) for ques in assignment_question_list]
                    ))

        assignment_in_db = Assignment(
            title=assignment.title,
            is_published=assignment.is_published,
            submission_last_date=assignment.submission_last_date,
            teacher_id=assignment.teacher_id,
            questions=assignment_question_list,
            classes=assignment_classes_list,
            students=assignment_students_list
        )
        assignment_in_db = assignment_dao.save(assignment_in_db)
        return self.__get_formatted_assignment(assignment_in_db)

    def update_assignment(self, assignment: UpdateAssignmentRequest):

        assignment_in_db = assignment_dao.find_by_id(assignment.id)
        if(assignment_in_db == None):
            raise HTTPException(
                401, detail="No assignment exists with the given id")

        # if(assignment_in_db.teacher_id != user_id):
        #     raise HTTPException(
        #         401, detail="Not authorized to update the assignment")

        assignment_classes_list, assignment_students_list = self.__update_assignment_classes(
            assignment.id, assignment_in_db.classes, assignment.classes)

        assignment_questions_list = self.__update_assignment_topics(
            assignment_in_db.questions, assignment.topics)

        self.__update_assignment_student_questions(
            assignment_students_list, assignment_questions_list)

        # assignment_students_list = self.__update_assignment_students(
        #     assignment_in_db.classes, assignment.classes)

        # assignment_question_list = [AssignmentQuestion(
        #     question_id=i.question_id, sequence_num=i.sequence_num) for i in assignment.questions]

        # assignment_classes_list = [AssignmentClass(class_id=i.class_id)
        #                            for i in assignment.classes]

        assignment_in_db.title = assignment.title
        assignment_in_db.is_published = assignment.is_published
        assignment_in_db.submission_last_date = assignment.submission_last_date
        assignment_in_db.questions = assignment_questions_list
        assignment_in_db.classes = assignment_classes_list
        assignment_in_db.students = assignment_students_list
        assignment_in_db = assignment_dao.save(assignment_in_db)

        # assignment_in_db = assignment_dao.save(assignment_in_db)

        return self.__get_formatted_assignment(assignment_in_db)

    def __update_assignment_topics(self, questions_in_db, topics_in_request):
        assignment_questions_list = []

        db_ques_mapping = {}
        for ques in questions_in_db:
            db_ques_mapping[(ques.question_id, ques.topic_code)] = ques

        for topic in topics_in_request:
            for ques in topic.questions:
                ques_in_db = db_ques_mapping.get(
                    (ques.question_id, topic.topic_code))
                if(ques_in_db == None):
                    assignment_questions_list.append(AssignmentQuestion(
                        question_id=ques.question_id,
                        sequence_num=ques.sequence_num,
                        tutor_available=ques.tutor_available,
                        topic_code=topic.topic_code,
                        topic_sequence_num=topic.topic_sequence_num,
                        topic_tutor_available=topic.tutor_available
                    ))
                else:
                    ques_in_db.sequence_num = ques.sequence_num
                    ques_in_db.tutor_available = ques.tutor_available
                    ques_in_db.topic_sequence_num = topic.topic_sequence_num
                    ques_in_db.topic_tutor_available = topic.tutor_available
                    assignment_questions_list.append(ques_in_db)

        # for req_ques in questions_in_request:
        #     if(db_ques_mapping.get((ques.question_id, ques.topic_code), None) == None):
        #         assignment_questions_list.append()

        # for req_ques in questions_in_request:
        #     for db_ques in questions_in_db:
        #         if(req_ques.question_id == db_ques.question_id):
        #             db_ques.sequence_num = req_ques.sequence_num
        #             db_ques.tutor_available = req_ques.tutor_available
        #             assignment_questions_list.append(db_ques)
        #             break
        #     else:
        #         print(req_ques)
        #         assignment_questions_list.append(AssignmentQuestion(
        #             question_id=req_ques.question_id,
        #             sequence_num=req_ques.sequence_num,
        #             tutor_available=req_ques.tutor_available))

        # print(assignment_questions_list)
        return assignment_questions_list

    def __update_assignment_classes(self, id, classes_in_db, classes_in_request):
        assignment_classes_list = []
        assignment_students_list = []
        for req_class in classes_in_request:
            for db_class in classes_in_db:
                if(req_class.class_id == db_class.class_id):
                    assignment_classes_list.append(db_class)
                    class_students = assignment_student_dao.find_students_by_assignment_id_and_class_id(
                        id, req_class.class_id)
                    assignment_students_list.extend(class_students)
                    break
            else:
                assignment_classes_list.append(
                    AssignmentClass(class_id=req_class.class_id))
                class_students = classroom_service.get_students(
                    req_class.class_id)
                for student in class_students:
                    assignment_students_list.append(
                        AssignmentStudent(
                            student_id=student["id"],
                            class_id=student["class_id"],
                            first_name=student["first_name"],
                            last_name=student["last_name"],
                            email=student["email"],
                            parents_email=student["parents_email"],
                            questions=[]
                        ))
        return assignment_classes_list, assignment_students_list

    def __update_assignment_student_questions(self, assignment_students_list, assignment_questions_list):
        for student in assignment_students_list:

            assignment_student_questions_list = []

            for questions_in_req in assignment_questions_list:
                for questions_in_db in student.questions:
                    if(questions_in_db.question_id == questions_in_req.question_id):
                        assignment_student_questions_list.append(
                            questions_in_db)
                        break
                else:
                    assignment_student_questions_list.append(
                        AssignmentStudentQuestion(question_id=questions_in_req.question_id))

            student.questions = assignment_student_questions_list

    def delete_assignment(self, assignment_id: int):
        assignment_in_db = assignment_dao.find_by_id(assignment_id)

        if(assignment_in_db == None):
            raise HTTPException(
                401, detail="No assignment exists with the given id")

        assignment_dao.delete(assignment_id)
        return HTTPException(status_code=204, detail="resource deleted successfully")

    def copy_assignment(self, assignment_id: int):
        assignment_in_db = assignment_dao.find_by_id(assignment_id)
        if(assignment_in_db == None):
            raise HTTPException(
                401, detail="No assignment exists with the given id")
        # if(assignment_in_db.teacher_id != user_id):
        #     raise HTTPException(401, detail="Not Authorized")

        new_assignment = assignment_dao.clone(assignment_in_db)

        return self.__get_formatted_assignment(new_assignment)

    def updateAssignmentStatus(self, updateAssignmentPublishStatusRequest: UpdateAssignmentPublishStatusRequest):
        assignment_in_db = assignment_dao.find_by_id(
            updateAssignmentPublishStatusRequest.id)
        if(assignment_in_db == None):
            raise HTTPException(
                401, detail="No assignment exists with the given id")
        # if(assignment_in_db.teacher_id != user_id):
        #     raise HTTPException(401, detail="Not Authorized")

        assignment_in_db.is_published = updateAssignmentPublishStatusRequest.is_published

        updated_assignment = assignment_dao.new_update(assignment_in_db)

        return self.__get_formatted_assignment(updated_assignment)

    def get_all_student_assignments(self, user_id: str):
        all_assignments_student_in_db = assignment_student_dao.find_assignments_by_student_id_and_is_published(
            user_id)

        completed = []
        active = []

        for assignment_student in all_assignments_student_in_db:
            completed_count, total_count = self.__get_completed_count(
                assignment_student.questions)

            assignemnt_details = BasicAssignementDetailsStudentResponse(
                assignment_id=assignment_student.assignment_id,
                title=assignment_student.assignment.title,
                progress="{completed_count}/{total_count}".format(
                    completed_count=completed_count, total_count=total_count),
                due_date=assignment_student.assignment.submission_last_date,
                late=False,
                completed=(assignment_student.status ==
                           AssignmentStatusEnum.COMPLETED)
            )

            if(assignment_student.status == AssignmentStatusEnum.COMPLETED):
                completed.append(assignemnt_details)
            else:
                active.append(assignemnt_details)

        return AllAssignmentStudentResponse(
            student_id=user_id,
            active=active,
            completed=completed
        )

    def complete_question(self, assignment_id, question_id, user_id):
        assignment_student = assignment_student_dao.find_assignment_student_by_assignment_id_and_student_id_and_is_published(
            assignment_id, user_id)

        if(assignment_student == None):
            raise HTTPException(
                401, detail="Not able to find assignment assigned to the student")

        for ques in assignment_student.questions:
            if(ques.question_id == question_id):
                ques.status = QuestionStatusEnum.SKIPPED
                ques.completed_at = datetime.utcnow()
                assignment_student_dao.save(assignment_student)
                break
        else:
            raise HTTPException(
                401, detail="Invalid Question Id")

    def __get_completed_count(self, questions_list):
        total_count = 0
        competed_count = 0
        for ques in questions_list:
            if(ques.status != QuestionStatusEnum.NOT_ATTEMPTED):
                competed_count += 1
            total_count += 1
        return competed_count, total_count


assignment_service = AssignmentService()
