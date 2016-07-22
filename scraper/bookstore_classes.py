from random import shuffle

class Bookstore(object):
    def __init__(self, name = None, url = None, ID = None):
        '''
        Bookstore class is made to contain the structure of a bookstore.
        '''
        self.name = name
        self.url = url
        self.ID = ID
        self.campuses = []
        self.structure_complete = 0
        self.books_complete = 0

    def add_attributes(self, name,url,ID):
        self.name = name
        self.url=url
        self.ID=ID

    def add_campus(self, campus_name, campus_ID):
        self.campuses.append(Campus(campus_name, campus_ID))

    def add_campuses_from_dict(self, campus_dict_list):
        if not len(self.campuses):
            for campus_dict in campus_dict_list:
                self.campuses.append(Campus(campus_dict['categoryName'], campus_dict['categoryId']))

    def get_campuses(self):
        return self.campuses

    def print_store(self):
        print self.name
        for campus in self.campuses:
            print '\t', campus.name
            for term in campus.terms:
                print '\t\t', term.name
                for department in term.departments:
                    print '\t\t\t', department.name
                    for course in department.courses:
                        print '\t\t\t\t', course.name
                        for section in course.sections:
                            print '\t\t\t\t\t', section.name

    def get_dict_repr(self):
        """
        Returns a dicionary representation of the store
        """
        return {'store_name':self.name,
                'url':self.url,
                'store_ID':self.ID,
                'structure_complete':self.structure_complete,
                'books_complete':self.books_complete,
                'campuses': [campus.get_dict_repr() for campus in self.campuses]
                }

    def load_from_dict(self,other):
        """
        Loads in a store's information, as formatted by get_dict_repr
        """
        if (other):
            self.name = other['store_name']
            self.ID = other['store_ID']
            self.url = other['url']
            self.structure_complete = other['structure_complete']
            self.books_complete=other['books_complete']
            self.campuses = [Campus().load_from_dict(campus) for campus in other['campuses']]
            return self

    def resume(self):
        """
        Returns ID of first incomplete store item, or false if all items are complete

        """
        for campus in self.campuses:
            if not len(campus.terms):
                return campus.ID
            for term in campus.terms:
                if  not len(term.departments):
                    return term.ID
                for department in term.departments:
                    if not len(department.courses):
                        return department.ID
                    for course in department.courses:
                        if not len(course.sections):
                            return course.ID
        return False

    def get_section_ids(self):
        """Returns all section IDs"""
        all_sections = []
        for campus in self.campuses:
            for term in campus.terms:
                for department in term.departments:
                    for course in department.courses:
                        for section in course.sections:
                            all_sections.append(section.ID)
        return all_sections

    def get_unknown_section_chunks(self,chunk_size=25):
        """
        Input: Chunk size (# of sections per book request page) to break sections into.
        Returns [[s1.id,s2.id],[s3.id,s4.id],...] for sections that are currently missing book information
        """
        all_sections = []
        for campus in self.campuses:
            for term in campus.terms:
                for department in term.departments:
                    for course in department.courses:
                        for section in course.sections:
                            if not section.books:
                                all_sections.append(section.ID)
        section_id_count = len(all_sections)
        all_chunks = []
        for i in range(0,section_id_count,chunk_size):
            if (i+chunk_size >= section_id_count):
                chunk = all_sections[i:]
                all_chunks.append(chunk)
            else:
                chunk = all_sections[i:i+chunk_size]
                all_chunks.append(chunk)
        if not all_chunks:
            all_chunks.append([])
        return all_chunks

    def get_all_sections(self):
        """
        Returns all sections
        """
        all_sections = []
        for campus in self.campuses:
            for term in campus.terms:
                for department in term.departments:
                    for course in department.courses:
                        for section in course.sections:
                            all_sections.append(section)
        return all_sections

    def get_row_lists(self, chunk_size):
        """
        Old version, no longer used
        """
        all_rows = []
        for campus in self.campuses:
            for term in campus.terms:
                for department in term.departments:
                    for course in department.courses:
                        for section in course.sections:
                            # only add rows that haven't been finished yet
                            if not section.books:
                                all_rows.append({'termID':term.ID,'department_name':department.name,'course_name':course.name,'sectionID':section.ID,'section_name':section.name})
        #shuffle to avoid pages full of no-book sections(results in error)
        shuffle(all_rows)
        section_id_count = len(all_rows)
        all_chunks = []
        for i in range(0,section_id_count,chunk_size):
            if (i+chunk_size >= section_id_count):
                chunk = all_rows[i:]
                all_chunks.append(chunk)
            else:
                chunk = all_rows[i:i+chunk_size]
                all_chunks.append(chunk)

        return all_chunks

    def add_books_from_dict(self,book_dicts):
        """
        Add books from a list of dicts with key:sectionID, val:list of books with info in dicts
        """
        books_copy = [x for x in book_dicts]
        for section in self.get_all_sections():
            for book_dict in books_copy:
                if book_dict.keys()[0] == section.ID:
                    section.books = [Book().load_from_dict(book) for book in book_dict.values()[0]]
                    break

        return False

    def get_resume_info(self):
        """
        No longer in use
        """
        resume = self.resume()
        if resume:
            for campus in self.campuses:
                if resume==campus.ID:
                    return (campus.name)
                for term in campus.terms:
                    if resume==term.ID:
                        return (campus.name, term.name)
                    for department in term.departments:
                        if resume==department.ID:
                            return (campus.name, term.name, department.name)
                        for course in department.courses:
                            if resume==course.ID:
                                return (campus.name, term.name, department.name, course.name)
                            for section in course.sections:
                                if resume==section.ID:
                                    return (ampus.name, term.name, department.name, course.name, section.name)
        return false
        
class Campus(object):
    def __init__(self, name=None, ID=None):
        self.name = name
        self.ID = ID
        self.terms = []

    def add_term(self, term_name, term_ID):
        self.terms.append(Term(term_name, term_ID))

    def add_terms_from_dict(self, term_dict_list):
        for term_dict in term_dict_list:
            self.terms.append(Term(term_dict['categoryName'], term_dict['categoryId']))

    def get_terms(self):
        return self.terms

    def get_dict_repr(self):
        return {'campus_name':self.name,'campus_ID':self.ID,'terms': [term.get_dict_repr() for term in self.terms]}

    def load_from_dict(self,other):
        self.name = other['campus_name']
        self.ID = other['campus_ID']
        self.terms = [Term().load_from_dict(term) for term in other['terms']]
        return self

class Term(object):
    def __init__(self, name=None, ID=None):
        self.name = name
        self.ID = ID
        self.departments = []

    def add_department(self, department_name, department_ID):
        self.departments.append(Department(department_name, department_ID))

    def get_departments(self):
        return self.departments

    def add_departments_from_dict(self, department_dict_list):
        for department_dict in department_dict_list:
            self.departments.append(Department(department_dict['categoryName'], department_dict['categoryId']))

    def get_dict_repr(self):
        return {'term_name':self.name,'term_ID':self.ID,'departments': [department.get_dict_repr() for department in self.departments]}

    def load_from_dict(self,other):
        self.name = other['term_name']
        self.ID = other['term_ID']
        self.departments = [Department().load_from_dict(department) for department in other['departments']]
        return self

class Department(object):
    def __init__(self, name=None, ID=None):
        self.name = name
        self.ID = ID
        self.courses = []

    def add_course(self, course_name, course_ID):
        self.courses.append(Course(course_name, course_ID))

    def add_courses_from_dict(self, course_dict_list):
        for course_dict in course_dict_list:
            self.courses.append(Course(course_dict['categoryName'], course_dict['categoryId']))

    def get_courses(self):
        return self.courses

    def get_dict_repr(self):
        return {'department_name':self.name,'department_ID':self.ID,'courses': [course.get_dict_repr() for course in self.courses]}

    def load_from_dict(self,other):
        self.name = other['department_name']
        self.ID = other['department_ID']
        self.courses = [Course().load_from_dict(course) for course in other['courses']]
        return self
class Course(object):
    def __init__(self, name=None, ID=None):
        self.name = name
        self.ID = ID
        self.sections = []

    def add_section(self, section_name, section_ID):
        self.sections.append(Section(section_name, section_ID))

    def add_sections_from_dict(self, section_dict_list):
        for section_dict in section_dict_list:
            self.sections.append(Section(section_dict['categoryName'], section_dict['categoryId']))

    def get_sections(self):
        return self.sections

    def get_dict_repr(self):
        return {'course_name':self.name,'course_ID':self.ID,'sections': [section.get_dict_repr() for section in self.sections]}

    def load_from_dict(self,other):
        self.name = other['course_name']
        self.ID = other['course_ID']
        self.sections = [Section().load_from_dict(section) for section in other['sections']]
        return self

class Section(object):
    def __init__(self, name=None, ID=None):
        self.name = name
        self.ID = ID
        self.books=[]

    def get_dict_repr(self):
        return {'section_name':self.name,'section_ID':self.ID, 'books':[book.get_dict_repr() for book in self.books]}

    def load_from_dict(self,other):
        self.name = other['section_name']
        self.ID = other['section_ID']
        if ('books' in other.keys()):
            self.books = [Book().load_from_dict(book) for book in other['books']]
        return self

class Book(object):
    def __init__(self, title=None, author=None, isbn=None,publisher=None, edition=None, rec_type=None, rent_used=None,rent_new=None,buy_used=None,buy_new=None):
        self.title = title
        self.author = author
        self.isbn = isbn
        self.publisher = publisher
        self.edition = edition
        self.rec_type = rec_type
        self.rent_used = rent_used
        self.rent_new = rent_new
        self.buy_used = buy_used
        self.buy_new = buy_new

    def get_dict_repr(self):
        return {'title':self.title,'author':self.author,'isbn':self.isbn,'publisher':self.publisher,'edition':self.edition,'rec_type':self.rec_type,'rent_used':self.rent_used,'rent_new':self.rent_new,'buy_used':self.buy_used,'buy_new':self.buy_new}

    def load_from_dict(self,other):
        self.title = other['title']
        self.author = other['author']
        self.isbn = other['isbn']
        self.publisher = other['publisher']
        self.edition = other['edition']
        self.rec_type = other['rec_type']
        self.rent_used = other['rent_used']
        self.rent_new = other['rent_new']
        self.buy_used = other['buy_used']
        self.buy_new = other['buy_new']
        return self
