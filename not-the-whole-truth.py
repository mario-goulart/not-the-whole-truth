### Primitives

NIL = []

T = True

def QUOTE(exp):
    return exp

def ATOM(exp):
    return not isinstance(exp, list)

def EQ(exp1, exp2):
    return exp1 == exp2

def CAR(exp):
    return exp[0]

def CDR(exp):
    return exp[1:]

def CONS(exp1, exp2):
    return [exp1] + exp2

# Native COND is Python's if/elif/else

### Helpers

def NULL(exp):
    return EQ(exp, NIL)

def CADR(exp):
    return CAR(CDR(exp))

def CADDR(exp):
    return CAR(CDR(CDR(exp)))

def CAAR(exp):
    return CAR(CAR(exp))

def CADAR(exp):
    return CAR(CDR(CAR(exp)))

def CADDAR(exp):
    return CAR(CDR(CDR(CAR(exp))))

def EVCOND(clauses, env):
    if EQ(EVAL(CAAR(clauses), env), T):
        return EVAL(CADAR(clauses), env)
    else:
        return EVCOND(CDR(clauses), env)

def ASSOC(e, a):
    if NULL(a):
        return NIL
    elif EQ(e, CAAR(a)):
        return CADR(CAR(a))
    else:
        return ASSOC(e, CDR(a))

def FFAPPEND(u, v):
    if NULL(u):
        return v
    else:
        return CONS(CAR(u), FFAPPEND(CDR(u), v))

def PAIRUP(u, v):
    if NULL(u):
        return NIL
    else:
        return CONS(CONS(CAR(u), CONS(CAR(v), NIL)),
                    PAIRUP(CDR(u), CDR(v)))

def EVLIS(u, a):
    if NULL(u):
        return NIL
    else:
        return CONS(EVAL(CAR(u), a),
                    EVLIS(CDR(u), a))

### The core

def EVAL(exp, env):
    if ATOM(exp):
        if EQ(exp, T):
            return T
        elif EQ(exp, NIL):
            return NIL
        else:
            return ASSOC(exp, env)
    elif ATOM(CAR(exp)):
        if EQ(CAR(exp), 'QUOTE'):
            return CADR(exp)
        elif EQ(CAR(exp), 'CAR'):
            return CAR(EVAL(CADR(exp), env))
        elif EQ(CAR(exp), 'CDR'):
            return CDR(EVAL(CADR(exp), env))
        elif EQ(CAR(exp), 'CADDR'):
            return CADDR(EVAL(CADR(exp), env))
        elif EQ(CAR(exp), 'CAAR'):
            return CAAR(EVAL(CADR(exp), env))
        elif EQ(CAR(exp), 'CADAR'):
            return CADAR(EVAL(CADR(exp), env))
        elif EQ(CAR(exp), 'ATOM'):
            return ATOM(EVAL(CADR(exp), env))
        elif EQ(CAR(exp), 'NULL'):
            return NULL(EVAL(CADR(exp), env))
        elif EQ(CAR(exp), 'CONS'):
            return CONS(EVAL(CADR(exp), env),
                        EVAL(CADDR(exp), env))
        elif EQ(CAR(exp), 'EQ'):
            return EQ(EVAL(cadr(exp), env),
                      EVAL(caddr(exp), env))
        elif EQ(CAR(exp), 'COND'):
            return EVCOND(CDR(exp), env)
        else:
            return EVAL(CONS(ASSOC(CAR(exp), env), CDR(exp)), env)
    elif EQ(CAAR(exp), 'LAMBDA'):
        return EVAL(CADDAR(exp),
                    FFAPPEND(PAIRUP(CADAR(exp), EVLIS(CDR(exp), env)), env))
    elif EQ(CAAR(exp), 'LABEL'):
        return EVAL(CONS(CADDAR(exp), CDR(exp)),
                    CONS(CONS(CADAR(exp), CONS(CAR(exp), NIL)), env))


# Some tests

def test(expr, expected, env=[]):
    result = EVAL(expr, env)
    print('[%s] %s %s => %s' %
          ('OK' if result == expected else 'FAIL',
           '' if result == expected else 'expected %s:' % expected,
           expr,
           result))

if 1:
    test('a', 2, env=[['a', 2]])
    test(['QUOTE', 'a'], 'a')
    test(['QUOTE', ['a']], ['a'])
    test(['CDR', ['QUOTE', ['a', 'b']]], ['b'])
    test(['CONS', ['QUOTE', 'foo'], ['QUOTE', ['bar']]], ['foo', 'bar'])
    test(['CONS', ['QUOTE', ['foo']], ['QUOTE', ['bar']]], [['foo'], 'bar'])
    test(['CONS', ['QUOTE', 'x'], ['QUOTE', ['y', 'z']]], ['x', 'y', 'z'])
    test(['COND', [T, ['QUOTE', 2]]], 2)
    test(['COND', [['NULL', ['QUOTE', 'foo']], ['QUOTE', 4]], [T, ['QUOTE', 2]]], 2)
    test([['LAMBDA', ['X'], ['CDR', 'X']], ['QUOTE', [1, 2]]], [2])
    test([['LABEL', 'FOO', ['LAMBDA', ['x'], 'x']], ['QUOTE', 4]], 4)
    test([['LABEL',
           'APPEND',
           ['LAMBDA', ['l1', 'l2'],
            ['COND',
             [['NULL', 'l1'], 'l2'],
             [T, ['CONS', ['CAR', 'l1'], ['APPEND', ['CDR', 'l1'], 'l2']]]]]],
          ['QUOTE', ['a', 'b', 'c']],
          ['QUOTE', ['d', 'e', 'f']]],
         ['a', 'b', 'c', 'd', 'e', 'f'])
