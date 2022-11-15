# global
import sys
import numpy as np
from hypothesis import strategies as st

# local
import ivy_tests.test_ivy.helpers as helpers
from ivy_tests.test_ivy.helpers import handle_frontend_test


# helpers
@st.composite
def _get_dtype_and_square_matrix(draw):
    dim_size = draw(helpers.ints(min_value=2, max_value=5))
    dtype = draw(helpers.get_dtypes("float", index=1, full=False))
    mat = draw(
        helpers.array_values(
            dtype=dtype[0], shape=(dim_size, dim_size), min_value=0, max_value=10
        )
    )
    return dtype, mat


@st.composite
def _get_dtype_input_and_vectors(draw, with_input=False, same_size=False):
    dim_size1 = draw(helpers.ints(min_value=2, max_value=5))
    dim_size2 = dim_size1 if same_size else draw(helpers.ints(min_value=2, max_value=5))
    dtype = draw(helpers.get_dtypes("float", index=1, full=False))
    vec1 = draw(
        helpers.array_values(
            dtype=dtype[0], shape=(dim_size1,), min_value=2, max_value=5
        )
    )
    vec2 = draw(
        helpers.array_values(
            dtype=dtype[0], shape=(dim_size2,), min_value=2, max_value=5
        )
    )
    if with_input:
        input = draw(
            helpers.array_values(
                dtype=dtype[0], shape=(dim_size1, dim_size2), min_value=2, max_value=5
            )
        )
        return dtype, input, vec1, vec2
    return dtype, vec1, vec2


@st.composite
def _get_dtype_input_and_matrices(draw, with_input=False):
    dim_size1 = draw(helpers.ints(min_value=2, max_value=5))
    dim_size2 = draw(helpers.ints(min_value=2, max_value=5))
    shared_size = draw(helpers.ints(min_value=2, max_value=5))
    dtype = draw(helpers.get_dtypes("float", index=1, full=False))
    mat1 = draw(
        helpers.array_values(
            dtype=dtype[0], shape=(dim_size1, shared_size), min_value=2, max_value=5
        )
    )
    mat2 = draw(
        helpers.array_values(
            dtype=dtype[0], shape=(shared_size, dim_size2), min_value=2, max_value=5
        )
    )
    if with_input:
        input = draw(
            helpers.array_values(
                dtype=dtype[0], shape=(dim_size1, dim_size2), min_value=2, max_value=5
            )
        )
        return dtype, input, mat1, mat2
    return dtype, mat1, mat2


@st.composite
def _get_dtype_and_3dbatch_matrices(draw, with_input=False, input_3d=False):
    dim_size1 = draw(helpers.ints(min_value=2, max_value=5))
    dim_size2 = draw(helpers.ints(min_value=2, max_value=5))
    shared_size = draw(helpers.ints(min_value=2, max_value=5))
    dtype = draw(helpers.get_dtypes("float", index=1, full=False))
    batch_size = draw(helpers.ints(min_value=2, max_value=4))
    mat1 = draw(
        helpers.array_values(
            dtype=dtype[0],
            shape=(batch_size, dim_size1, shared_size),
            min_value=2,
            max_value=5,
        )
    )
    mat2 = draw(
        helpers.array_values(
            dtype=dtype[0],
            shape=(batch_size, shared_size, dim_size2),
            min_value=2,
            max_value=5,
        )
    )
    if with_input:
        if input_3d:
            input = draw(
                helpers.array_values(
                    dtype=dtype[0],
                    shape=(batch_size, dim_size1, dim_size2),
                    min_value=2,
                    max_value=5,
                )
            )
            return dtype, input, mat1, mat2
        input = draw(
            helpers.array_values(
                dtype=dtype[0], shape=(dim_size1, dim_size2), min_value=2, max_value=5
            )
        )
        return dtype, input, mat1, mat2
    return dtype, mat1, mat2


@st.composite
def _get_dtype_input_and_mat_vec(draw, *, with_input=False, skip_float16=False):
    dim_size = draw(helpers.ints(min_value=2, max_value=5))
    shared_size = draw(helpers.ints(min_value=2, max_value=5))
    dtype = draw(helpers.get_dtypes("float", index=1, full=True))

    if skip_float16:
        dtype = tuple(set(dtype).difference({"float16"}))

    dtype = draw(st.sampled_from(dtype))

    mat = draw(
        helpers.array_values(
            dtype=dtype, shape=(dim_size, shared_size), min_value=2, max_value=5
        )
    )
    vec = draw(
        helpers.array_values(
            dtype=dtype, shape=(shared_size,), min_value=2, max_value=5
        )
    )
    if with_input:
        input = draw(
            helpers.array_values(
                dtype=dtype, shape=(dim_size,), min_value=2, max_value=5
            )
        )
        return [dtype], input, mat, vec
    return [dtype], mat, vec


# addbmm
@handle_frontend_test(
    fn_tree="torch.addbmm",
    dtype_and_matrices=_get_dtype_and_3dbatch_matrices(with_input=True),
    beta=st.floats(
        min_value=-5,
        max_value=5,
        allow_nan=False,
        allow_subnormal=False,
        allow_infinity=False,
    ),
    alpha=st.floats(
        min_value=-5,
        max_value=5,
        allow_nan=False,
        allow_subnormal=False,
        allow_infinity=False,
    ),
)
def test_torch_addbmm(
    *,
    dtype_and_matrices,
    beta,
    alpha,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, input, mat1, mat2 = dtype_and_matrices
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-01,
        input=input,
        batch1=mat1,
        batch2=mat2,
        beta=beta,
        alpha=alpha,
    )


# addmm
@handle_frontend_test(
    fn_tree="torch.addmm",
    dtype_and_matrices=_get_dtype_input_and_matrices(with_input=True),
    beta=st.floats(
        min_value=-5,
        max_value=5,
        allow_nan=False,
        allow_subnormal=False,
        allow_infinity=False,
    ),
    alpha=st.floats(
        min_value=-5,
        max_value=5,
        allow_nan=False,
        allow_subnormal=False,
        allow_infinity=False,
    ),
)
def test_torch_addmm(
    *,
    dtype_and_matrices,
    beta,
    alpha,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, input, mat1, mat2 = dtype_and_matrices
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-01,
        input=input,
        mat1=mat1,
        mat2=mat2,
        beta=beta,
        alpha=alpha,
    )


# addmv
@handle_frontend_test(
    fn_tree="torch.addmv",
    dtype_and_matrices=_get_dtype_input_and_mat_vec(with_input=True, skip_float16=True),
    beta=st.floats(
        min_value=-5,
        max_value=5,
        allow_nan=False,
        allow_subnormal=False,
        allow_infinity=False,
    ),
    alpha=st.floats(
        min_value=-5,
        max_value=5,
        allow_nan=False,
        allow_subnormal=False,
        allow_infinity=False,
    ),
)
def test_torch_addmv(
    *,
    dtype_and_matrices,
    beta,
    alpha,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, input, mat, vec = dtype_and_matrices
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-03,
        input=input,
        mat=mat,
        vec=vec,
        beta=beta,
        alpha=alpha,
    )


# addr
@handle_frontend_test(
    fn_tree="torch.addr",
    dtype_and_vecs=_get_dtype_input_and_vectors(with_input=True),
    beta=st.floats(
        min_value=-5,
        max_value=5,
        allow_nan=False,
        allow_subnormal=False,
        allow_infinity=False,
    ),
    alpha=st.floats(
        min_value=-5,
        max_value=5,
        allow_nan=False,
        allow_subnormal=False,
        allow_infinity=False,
    ),
)
def test_torch_addr(
    *,
    dtype_and_vecs,
    beta,
    alpha,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, input, vec1, vec2 = dtype_and_vecs

    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-01,
        input=input,
        vec1=vec1,
        vec2=vec2,
        beta=beta,
        alpha=alpha,
    )


# baddbmm
@handle_frontend_test(
    fn_tree="torch.baddbmm",
    dtype_and_matrices=_get_dtype_and_3dbatch_matrices(with_input=True, input_3d=True),
    beta=st.floats(
        min_value=-5,
        max_value=5,
        allow_nan=False,
        allow_subnormal=False,
        allow_infinity=False,
    ),
    alpha=st.floats(
        min_value=-5,
        max_value=5,
        allow_nan=False,
        allow_subnormal=False,
        allow_infinity=False,
    ),
)
def test_torch_baddbmm(
    *,
    dtype_and_matrices,
    beta,
    alpha,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, input, batch1, batch2 = dtype_and_matrices

    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-01,
        input=input,
        batch1=batch1,
        batch2=batch2,
        beta=beta,
        alpha=alpha,
    )


# bmm
@handle_frontend_test(
    fn_tree="torch.bmm",
    dtype_and_matrices=_get_dtype_and_3dbatch_matrices(),
)
def test_torch_bmm(
    *,
    dtype_and_matrices,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, mat1, mat2 = dtype_and_matrices
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-02,
        input=mat1,
        mat2=mat2,
    )


# cholesky
@handle_frontend_test(
    fn_tree="torch.cholesky",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float", index=1, full=True),
        min_value=0,
        max_value=10,
        shape=helpers.ints(min_value=2, max_value=5).map(lambda x: tuple([x, x])),
    ).filter(
        lambda x: np.linalg.cond(x[1]) < 1 / sys.float_info.epsilon
        and np.linalg.det(np.asarray(x[1])) != 0
    ),
    upper=st.booleans(),
)
def test_torch_cholesky(
    *,
    dtype_and_x,
    upper,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    x = x[0]
    x = (
        np.matmul(x.T, x) + np.identity(x.shape[0]) * 1e-3
    )  # make symmetric positive-definite
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-02,
        input=x,
        upper=upper,
    )


# ger
@handle_frontend_test(
    fn_tree="torch.ger",
    dtype_and_vecs=_get_dtype_input_and_vectors(),
)
def test_torch_ger(
    *,
    dtype_and_vecs,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, vec1, vec2 = dtype_and_vecs
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        input=vec1,
        vec2=vec2,
    )


# inverse
@handle_frontend_test(
    fn_tree="torch.inverse",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float", index=1, full=True),
        min_value=0,
        max_value=25,
        shape=helpers.ints(min_value=2, max_value=10).map(lambda x: tuple([x, x])),
    ).filter(lambda x: np.linalg.cond(x[1]) < 1 / sys.float_info.epsilon),
)
def test_torch_inverse(
    *,
    dtype_and_x,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-03,
        input=x[0],
    )


# det
@handle_frontend_test(
    fn_tree="torch.det",
    dtype_and_x=_get_dtype_and_square_matrix(),
)
def test_torch_det(
    *,
    dtype_and_x,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        input=x,
    )


# logdet
@handle_frontend_test(
    fn_tree="torch.logdet",
    dtype_and_x=_get_dtype_and_square_matrix(),
)
def test_torch_logdet(
    *,
    dtype_and_x,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        input=x,
    )


# slogdet
@handle_frontend_test(
    fn_tree="torch.slogdet",
    dtype_and_x=_get_dtype_and_square_matrix(),
)
def test_torch_slogdet(
    *,
    dtype_and_x,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        input=x,
    )


# matmul
@handle_frontend_test(
    fn_tree="torch.matmul",
    dtype_xy=_get_dtype_and_3dbatch_matrices(),
)
def test_torch_matmul(
    *,
    dtype_xy,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x, y = dtype_xy
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-02,
        input=x,
        other=y,
        out=None,
    )


# matrix_power
@handle_frontend_test(
    fn_tree="torch.matrix_power",
    dtype_and_x=_get_dtype_and_square_matrix(),
    n=helpers.ints(min_value=2, max_value=5),
)
def test_torch_matrix_power(
    *,
    dtype_and_x,
    n,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-01,
        input=x,
        n=n,
    )


# matrix_rank
@handle_frontend_test(
    fn_tree="torch.matrix_rank",
    dtype_and_x=_get_dtype_and_square_matrix(),
    rtol=st.floats(1e-05, 1e-03),
    sym=st.booleans(),
)
def test_torch_matrix_rank(
    *,
    dtype_and_x,
    rtol,
    sym,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-01,
        input=x,
        tol=rtol,
        symmetric=sym,
    )


# mm
@handle_frontend_test(
    fn_tree="torch.mm",
    dtype_xy=_get_dtype_input_and_matrices(),
)
def test_torch_mm(
    *,
    dtype_xy,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x, y = dtype_xy
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        atol=1e-02,
        rtol=1e-02,
        input=x,
        mat2=y,
    )


# mv
@handle_frontend_test(
    fn_tree="torch.mv",
    dtype_mat_vec=_get_dtype_input_and_mat_vec(skip_float16=True),
)
def test_torch_mv(
    *,
    dtype_mat_vec,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, mat, vec = dtype_mat_vec
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-03,
        input=mat,
        vec=vec,
        out=None,
    )


# outer
@handle_frontend_test(
    fn_tree="torch.outer",
    dtype_and_vecs=_get_dtype_input_and_vectors(),
)
def test_torch_outer(
    *,
    dtype_and_vecs,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, vec1, vec2 = dtype_and_vecs
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        input=vec1,
        vec2=vec2,
    )


# pinverse
@handle_frontend_test(
    fn_tree="torch.pinverse",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float", index=1, full=True),
        min_num_dims=2,
        max_num_dims=2,
        min_dim_size=2,
        max_dim_size=5,
    ),
    rtol=st.floats(1e-5, 1e-3),
)
def test_torch_pinverse(
    *,
    dtype_and_x,
    rtol,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-03,
        input=x[0],
        rcond=rtol,
    )


# qr
@handle_frontend_test(
    fn_tree="torch.qr",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float", index=1, full=True),
        min_num_dims=2,
        max_num_dims=2,
        min_dim_size=2,
        max_dim_size=5,
        min_value=2,
        max_value=5,
    ),
    some=st.booleans(),
)
def test_torch_qr(
    *,
    dtype_and_x,
    some,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        rtol=1e-02,
        input=x[0],
        some=some,
    )


# svd
@handle_frontend_test(
    fn_tree="torch.svd",
    dtype_and_x=helpers.dtype_and_values(
        available_dtypes=helpers.get_dtypes("float", index=1, full=True),
        min_num_dims=3,
        max_num_dims=5,
        min_dim_size=2,
        max_dim_size=5,
    ),
    some=st.booleans(),
    compute=st.booleans(),
)
def test_torch_svd(
    *,
    dtype_and_x,
    some,
    compute,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, x = dtype_and_x
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        input=x[0],
        some=some,
        compute_uv=compute,
    )


# vdot
@handle_frontend_test(
    fn_tree="torch.vdot",
    dtype_and_vecs=_get_dtype_input_and_vectors(same_size=True),
)
def test_torch_vdot(
    *,
    dtype_and_vecs,
    as_variable,
    with_out,
    num_positional_args,
    native_array,
    on_device,
    fn_tree,
    frontend,
):
    dtype, vec1, vec2 = dtype_and_vecs
    helpers.test_frontend_function(
        input_dtypes=dtype,
        as_variable_flags=as_variable,
        with_out=with_out,
        num_positional_args=num_positional_args,
        native_array_flags=native_array,
        frontend=frontend,
        fn_tree=fn_tree,
        on_device=on_device,
        input=vec1,
        other=vec2,
    )