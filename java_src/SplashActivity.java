package finanzasapp; // Asegúrate de que este paquete coincide con tu package name en buildozer.spec

import android.os.Bundle;
import com.airbnb.lottie.LottieAnimationView;
import org.kivy.android.PythonActivity;
import android.widget.FrameLayout;
import android.view.ViewGroup.LayoutParams;

public class SplashActivity extends PythonActivity {
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Crear un LottieAnimationView
        LottieAnimationView animationView = new LottieAnimationView(this);
        animationView.setAnimation("raw/splash_animation.json"); // Ruta relativa en el APK
        animationView.loop(true);
        animationView.playAnimation();

        // Configurar el layout
        FrameLayout layout = new FrameLayout(this);
        layout.setLayoutParams(new FrameLayout.LayoutParams(
            LayoutParams.MATCH_PARENT,
            LayoutParams.MATCH_PARENT
        ));
        layout.addView(animationView);

        // Establecer el layout como contenido de la actividad
        setContentView(layout);

        // Duración de la splash screen (por ejemplo, 3 segundos)
        animationView.postDelayed(new Runnable() {
            @Override
            public void run() {
                // Iniciar la actividad principal de Kivy
                finish(); // Cerrar la splash screen
            }
        }, 3000); // 3000 milisegundos = 3 segundos
    }
}
